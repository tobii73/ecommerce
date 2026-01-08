from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime, timezone
from app.database import get_db
from app.core.depends import (get_current_user,verify_business_ownership, require_seller)
from app.schemas.business import BusinessCreate, BusinessResponse, BusinessUpdate # Asegúrate de tener estos schemas

router = APIRouter(
    prefix="/business",
    tags=["Business"]
)

@router.post("/add", response_model=BusinessResponse, status_code=status.HTTP_201_CREATED)
async def add_business(request: BusinessCreate, db = Depends(get_db), current_user = Depends(get_current_user)):
    # Preparamos el documento del negocio
    new_business = request.model_dump()
    new_business["owner_id"] = str(current_user["_id"])
    new_business["created_at"] = datetime.now(timezone.utc)
    # Vinculamos el negocio al usuario que tiene la sesión activa
    
    result = await db["businesses"].insert_one(new_business)


    # Actualizar el rol
    if current_user.get("role") == "customer":
        await db["users"].update_one(
            {"_id": ObjectId(current_user["_id"])},
            {"$set": {"role": "seller"}}
        )
        

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


@router.put("/update/{business_id}", response_model=BusinessResponse)
async def update_business(business_id:str,request: BusinessUpdate ,db = Depends(get_db), current_user = Depends(require_seller), _ = Depends(verify_business_ownership())):

    business = await db["businesses"].find_one({"_id": ObjectId(business_id)})


    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    
    if business["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para modificar este negocio"
        )

    updated_data = {k: v for k, v in request.model_dump().items() if v is not None}
    if updated_data:
        updated_data["updated_at"] = datetime.now(timezone.utc)


    await db["businesses"].update_one({"_id": ObjectId(business_id)}, {"$set": updated_data})

    updated_business = await db["businesses"].find_one({"_id": ObjectId(business_id)})
    updated_business["_id"] = str(updated_business["_id"])
    return updated_business


# 3. Eliminar un negocio (DELETE /business/delete/{id})
@router.delete("/delete/{business_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_business(business_id: str, db = Depends(get_db), current_user = Depends(get_current_user), _ = Depends(verify_business_ownership())):
    # Buscamos el negocio por su ID de MongoDB
    business = await db["businesses"].find_one({"_id": ObjectId(business_id)})
    
    if not business:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Negocio no encontrado")
    
    # Verificación de seguridad: solo el dueño puede borrar su negocio
    if business["owner_id"] != str(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="No tienes permisos para eliminar este negocio"
        )

    await db["businesses"].delete_one({"_id": ObjectId(business_id)})
    return {"message": "Negocio eliminado correctamente"}