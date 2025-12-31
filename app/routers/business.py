from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from app.database import get_db
from app.core.auth import get_current_user
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate # Asegúrate de tener estos schemas

router = APIRouter(
    prefix="/business",
    tags=["Business"]
)

@router.post("/add", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def add_business(request: BusinessCreate, db = Depends(get_db), current_user = Depends(get_current_user)):
    # Preparamos el documento del negocio
    new_business = request.model_dump()
    # Vinculamos el negocio al usuario que tiene la sesión activa
    new_business["owner_id"] = str(current_user["_id"]) 
    
    result = await db["businesses"].insert_one(new_business)
    
    # Recuperamos y formateamos el resultado para evitar errores de tipo con el _id
    created_business = await db["businesses"].find_one({"_id": result.inserted_id})
    created_business["_id"] = str(created_business["_id"])
    return created_business

@router.get("/get", response_model=List[BusinessResponse])
async def get_all_businesses(db = Depends(get_db)):
    # Recuperamos todos los negocios registrados en el sistema
    businesses_cursor = db["businesses"].find()
    businesses = await businesses_cursor.to_list(length=100)
    
    for biz in businesses:
        biz["_id"] = str(biz["_id"])
    return businesses


@router.put("/update/{id}", response_model=BusinessResponse)
async def update_business(id:str,request: BusinessUpdate ,db = Depends(get_db), current_user = Depends(get_current_user)):

    business = await db["businesses"].find_one({"_id": ObjectId(id)})


    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    
    if business["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para modificar este negocio"
        )

    updated_data = {k: v for k, v in request.model_dump().items() if v is not None}
    await db["businesses"].update_one({"_id": ObjectId(id)}, {"$set": updated_data})

    updated_business = await db["businesses"].find_one({"_id": ObjectId(id)})
    updated_business["_id"] = str(updated_business["_id"])
    return updated_business


@router.delete("/delete/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(id: str, db = Depends(get_db), current_user = Depends(get_current_user)):
    # Buscamos el negocio por su ID de MongoDB
    business = await db["businesses"].find_one({"_id": ObjectId(id)})
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    
    # Verificación de seguridad: solo el dueño puede borrar su negocio
    if business["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para eliminar este negocio"
        )

    await db["businesses"].delete_one({"_id": ObjectId(id)})
    return {"message": "Negocio eliminado correctamente"}