from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from ..schemas.users import TokenData
from dotenv import load_dotenv
import os
load_dotenv()

pwd_context=CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2=OAuth2PasswordBearer(tokenUrl="/user/login")

SECRET_KEY = os.getenv("KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30
REFRESH_TOKEN_DURATION = 7
class Hash():
    
    @staticmethod
    def bcrypt(password: str) -> str:
        """
        Hashea una contraseña de forma segura para bcrypt.
        Bcrypt tiene un límite de 72 bytes, así que truncamos si es necesario.
        """
        # Bcrypt soporta máximo 72 bytes
        MAX_BCRYPT_BYTES = 72
        
        # Verificar longitud en bytes
        password_bytes = password.encode('utf-8')
        
        if len(password_bytes) > MAX_BCRYPT_BYTES:
            # Truncar a 72 bytes manteniendo caracteres válidos
            truncated_bytes = password_bytes[:MAX_BCRYPT_BYTES]
            
            # Intentar decodificar de vuelta a string
            try:
                # Decodificar ignorando bytes incompletos al final
                truncated_password = truncated_bytes.decode('utf-8', 'ignore')
                # Si quedó vacío, usar un fallback
                if not truncated_password:
                    # Tomar primeros 50 caracteres como fallback seguro
                    truncated_password = password[:50]
            except UnicodeDecodeError:
                # Si falla la decodificación, usar slice simple
                truncated_password = password[:50]
            
            # Usar la versión truncada
            password = truncated_password
        
        return pwd_context.hash(password)
    
    @staticmethod
    def verify(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_DURATION)
    
    to_encode.update({"exp": expire, "type": "access"})  # Agregar tipo
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    """
    Crea un refresh token válido por REFRESH_TOKEN_DURATION días
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_DURATION)
    
    # Refresh tokens tienen tipo "refresh" para diferenciarlos
    to_encode.update({"exp": expire, "type": "refresh"})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def refresh_access_token(refresh_token: str, db):

    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_token(refresh_token, credential_exception, expected_type="refresh")

    # 2. Buscar usuario en la base de datos
    user = await db["users"].find_one({"email": token_data.email})
    if user is None:
        raise credential_exception

    if user.get("refresh_token") != refresh_token:
        raise HTTPException(401, "Refresh token revocado")

    # 4. Crear NUEVO access token
    new_access_token = create_access_token(data={"sub": user["email"]})

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }

def verify_token(token: str, credential_exception, expected_type: str = None):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str=payload.get("sub")
        token_type: str = payload.get("type")

        if email is None:
            raise credential_exception
        

        # Si se especifica un tipo, verificar que coincida
        if expected_type and token_type != expected_type:
            raise credential_exception

        return TokenData(email=email, token_type=token_type)
    except JWTError:
        raise credential_exception


