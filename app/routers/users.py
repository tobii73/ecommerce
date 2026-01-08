from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.users import UserCreate, UserLogin, UserResponse, UserRole
from ..core.auth import Hash, create_access_token
from ..core.depends import get_current_user
from typing import List
from app.database import get_db
from bson import ObjectId

router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={status.HTTP_404_NOT_FOUND: {"message":"No encontrado"}}
)


@router.post("/registration", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registration(request: UserCreate, db = Depends(get_db)):
    existing_user = await db["users"].find_one({"email": request.email})
    if existing_user:
        raise HTTPException(400, "Usuario ya existe")
    
    user_data = request.model_dump(exclude={"password"})
    
    user_data["password"] = Hash.bcrypt(request.password)
    user_data["role"] = "customer"
    
    
    result = await db["users"].insert_one(user_data)
    
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    
    created_user["_id"] = str(created_user["_id"])
    return created_user


@router.post("/login")
async def login(request: UserLogin, db = Depends(get_db)):
    # Buscar al usuario por el email
    user = await db["users"].find_one({"email": request.email})
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Credenciales inválidas"
        )
    
    # Verificar contraseña con tu clase Hash
    if not Hash.verify(request.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta"
        )
    
    # Generar el Token JWT usando tu función
    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}

# 3. Obtener Usuarios (Basado en GET /user/users) [1]
# Opcional: puedes protegerlo con Depends(get_current_user)
@router.get("/users", response_model=List[UserResponse])
async def get_all_users(db = Depends(get_db), _ = Depends(get_current_user)):
    users_cursor = db["users"].find()
    users = await users_cursor.to_list(length=100)
    
    # IMPORTANTE: Formatear los documentos para que coincidan con el schema
    formatted_users = []
    for user in users:
        formatted_users.append({
            "_id": str(user["_id"]), 
            "username": user.get("username", ""),
            "email": user.get("email", "")
        })
    
    return formatted_users



@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user = Depends(get_current_user)):
    """Obtener el perfil del usuario actual"""
    return current_user

@router.put("/me/update-role")
async def update_my_role(
    new_role: UserRole,
    db = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Solo admin puede cambiar roles (para gestión)"""
    # Verificar que sea admin
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Solo admin puede cambiar roles")
    
    await db["users"].update_one(
        {"_id": ObjectId(current_user["_id"])},
        {"$set": {"role": new_role}}
    )
    
    return {"message": f"Rol actualizado a {new_role}"}


