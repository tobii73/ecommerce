from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timezone
from bson import ObjectId
from app.database import get_db
from app.core.auth import Hash
import os 
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("KEY")
ALGORITHM = "HS256"


# Configuración OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db = Depends(get_db)
) -> dict:

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decodificar token
        payload = jwt.decode(
            token, 
            SECRET_KEY, 
            algorithms=[ALGORITHM]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        # Verificar expiración
        exp = payload.get("exp")
        if exp and datetime.now(timezone.utc) > datetime.fromtimestamp(exp, tz=timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expirado"
            )
            
    except JWTError:
        raise credentials_exception
    
    # Buscar usuario en MongoDB
    user = await db["users"].find_one({"email": email})
    if user is None:
        raise credentials_exception
    
    # Convertir ObjectId a string y asegurar campos
    user["_id"] = str(user["_id"])
    user.setdefault("role", "customer")  # Backward compatibility
    
    return user


def require_role(required_role: str):
    """
    Factory que crea dependencias para verificar roles específicos.
    
    Ejemplo de uso en endpoint:
    @router.post("/products/add", dependencies=[Depends(require_role("seller"))])
    async def add_product(...):
        # Solo sellers pueden acceder
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere rol: {required_role}. Tu rol: {current_user.get('role')}"
            )
        return current_user
    return role_checker


def require_any_role(allowed_roles: list):
    """
    Verifica que el usuario tenga AL MENOS UNO de los roles permitidos.
    
    Ejemplo:
    @router.get("/reports", dependencies=[Depends(require_any_role(["admin", "moderator"]))])
    """
    def role_checker(current_user: dict = Depends(get_current_user)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requiere uno de estos roles: {allowed_roles}"
            )
        return current_user
    return role_checker


# async def get_current_user_optional(
#     token: str = Depends(oauth2_scheme),
#     db = Depends(get_db)
# ) -> dict | None:
#     """
#     Versión opcional de get_current_user.
#     Retorna el usuario si el token es válido, None si no.
    
#     Útil para endpoints que funcionan tanto para usuarios autenticados como anónimos.
    
#     Ejemplo:
#     @router.get("/products")
#     async def get_products(current_user = Depends(get_current_user_optional)):
#         if current_user:
#             Mostrar precios especiales para usuarios logueados
#         else:
#             Precios normales
#     """
#     try:
#         return await get_current_user(token, db)
#     except HTTPException:
#         return None


def verify_business_ownership():
    """
    Verifica que el usuario sea dueño del negocio.
    
    Ejemplo:
    @router.put("/business/{business_id}/update")
    async def update_business(
        business_id: str,
        current_user = Depends(verify_business_ownership(business_id))
    ):
        # current_user ya está verificado como dueño
    """
    async def ownership_checker(
        business_id: str,
        current_user: dict = Depends(get_current_user),
        db = Depends(get_db)
    ):
        
         # Verificar que business_id sea un string válido
        if not business_id or not isinstance(business_id, str):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="ID de negocio inválido"
            )
        
        business = await db["businesses"].find_one({
            "_id": ObjectId(business_id),
            "owner_id": str(current_user["_id"])
        })
        
        if not business:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No eres dueño de este negocio o no existe"
            )
        
        return current_user
    
    return ownership_checker


def verify_product_ownership():
    """
    Verifica que el usuario sea dueño del producto.
    Similar a verify_business_ownership pero para productos.
    """
    async def ownership_checker(
        product_id: str,
        current_user: dict = Depends(get_current_user),
        db = Depends(get_db)
    ):
        product = await db["products"].find_one({
            "_id": ObjectId(product_id),
            "owner_id": str(current_user["_id"])
        })
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No eres dueño de este producto o no existe"
            )
        
        return current_user
    
    return ownership_checker


# Dependencias pre-configuradas para roles comunes (conveniencia)
require_seller = require_role("seller")
require_admin = require_role("admin")
require_customer = require_role("customer")

# Dependencia para admin o seller
require_admin_or_seller = require_any_role(["admin", "seller"])