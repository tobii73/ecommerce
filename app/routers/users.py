from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.users import UserCreate, UserLogin, UserResponse, RefreshTokenRequest
from ..core.auth import Hash, get_current_user,create_access_token, create_refresh_token,refresh_access_token
from typing import List
from app.database import get_db


router = APIRouter(
    prefix="/user",
    tags=["user"],
    responses={status.HTTP_404_NOT_FOUND: {"message":"No encontrado"}}
)



@router.post("/registration", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def registration(request: UserCreate, db = Depends(get_db)):
    # Verificar si el usuario ya existe en MongoDB
    existing_user = await db["users"].find_one({"email": request.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )
    
    # Crear el diccionario del nuevo usuario usando tu clase Hash
    new_user = {
        "username": request.username,
        "email": request.email,
        "password": Hash.bcrypt(request.password) # Usamos tu método de hasheo
    }
    
    # Insertar en la colección de MongoDB
    result = await db["users"].insert_one(new_user)
    
    # Recuperar el usuario creado para devolverlo (mapeando el _id)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    # CONVERSIÓN NECESARIA:
    created_user["_id"] = str(created_user["_id"]) 
    return created_user


@router.post("/login")
async def login(request: UserLogin, db = Depends(get_db)):
    # Buscar al usuario por el email (que es lo que usa tu sub en el token)
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
    
    refresh_token = create_refresh_token(data={"sub": user["email"]})

    await db["users"].update_one(
        {"_id": user["_id"]},
        {"$set": {"refresh_token": refresh_token}}
    )
    return {"access_token": access_token,"refresh_token":refresh_token ,"token_type": "bearer"}



@router.post("/refresh")
async def refresh_token(refresh_request: RefreshTokenRequest,db = Depends(get_db)):

    refresh_token = refresh_request.refresh_token

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token requerido"
        )
    
    try:
        # Usar la función refresh_access_token de auth.py
        tokens = await refresh_access_token(refresh_token, db)
        return tokens
    except HTTPException as e:
        # Re-lanzar excepciones HTTP que ya vienen con formato correcto
        raise e
    except Exception as e:
        # Capturar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error renovando token: {str(e)}"
        )

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(db = Depends(get_db), _ = Depends(get_current_user)):
    users_cursor = db["users"].find()
    users = await users_cursor.to_list(length=100)
    
    # IMPORTANTE: Formatear los documentos para que coincidan con el schema
    formatted_users = []
    for user in users:
        formatted_users.append({
            "_id": str(user["_id"]),  # <-- Usar '_id' porque el alias así lo espera
            "username": user.get("username", ""),
            "email": user.get("email", "")
        })
    
    return formatted_users








# @router.get("/users", response_model=List[UserResponse])
# async def get_all_users(db = Depends(get_db), current_user = Depends(get_current_user)):
#     # Recuperar todos los documentos de la colección "users"
#     users_cursor = db["users"].find()
#     users = await users_cursor.to_list(length=100)
#     return users