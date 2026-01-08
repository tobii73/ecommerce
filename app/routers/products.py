from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from app.database import get_db
from app.core.depends import (get_current_user, verify_product_ownership, require_seller, require_customer)
from datetime import datetime, timezone
from app.schemas.products import ProductCreate, ProductUpdate, ProductResponse

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# 1. Agregar un nuevo producto (POST /products/add)
@router.post("/add", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def add_product(request: ProductCreate, db = Depends(get_db), current_user = Depends(require_seller) ):
    # Verificamos que el negocio (business_id) exista y pertenezca al usuario
    business = await db["businesses"].find_one({
        "owner_id": str(current_user["_id"])
    })

    
    if not business:
        raise HTTPException(status_code=404, detail="El negocio especificado no existe")
    
    if business["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="No tienes permiso para añadir productos a este negocio")
    
    if request.stock == 0:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Stock mínimo: 1 unidad")


    new_product = request.model_dump()
    new_product["owner_id"] = str(current_user["_id"])
    new_product["business_id"] = str(business["_id"])
    new_product["created_at"] = datetime.now(timezone.utc)
    new_product["update_at"]= datetime.now(timezone.utc)
    
    
    result = await db["products"].insert_one(new_product)
    created_product = await db["products"].find_one({"_id": result.inserted_id})
    
    # Convertimos el ID para evitar el error de serialización JSON 
    created_product["_id"] = str(created_product["_id"])
    return created_product

# 2. Obtener todos los productos (GET /products/get)
@router.get("/get", response_model=List[ProductResponse])
async def get_all_products(db = Depends(get_db)):
    # Recupera todos los productos sin necesidad de autenticación (catálogo público)
    products_cursor = db["products"].find()
    products = await products_cursor.to_list(length=100)
    
    for product in products:
        product["_id"] = str(product["_id"])
    return products

# 3. Actualizar un producto (PUT /products/update/{id})
@router.put("/update/{product_id}", response_model=ProductResponse)
async def update_product( 
    product_id: str,
    request: ProductUpdate,
    db = Depends(get_db),
    current_user = Depends(require_seller),
     _ = Depends(verify_product_ownership())
):
    product = await db["products"].find_one({"_id": ObjectId(product_id)})

    
    if not product or product["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="No autorizado para editar este producto")

    updated_data = {k: v for k, v in request.model_dump().items() if v is not None}
    
    if updated_data:
        updated_data["updated_at"] = datetime.now(timezone.utc)

    await db["products"].update_one({"_id": ObjectId(product_id),"owner_id": str(current_user["_id"])}, {"$set": updated_data})


    
    updated_product = await db["products"].find_one({"_id": ObjectId(product_id)})
    updated_product["_id"] = str(updated_product["_id"])
    return updated_product

# 4. Eliminar un producto (DELETE /products/delete/{id})
@router.delete("/delete/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db = Depends(get_db), current_user = Depends(require_seller), _ = Depends(verify_product_ownership())):
    product = await db["products"].find_one({"_id": ObjectId(product_id)})
    
    if not product or product["owner_id"] != str(current_user["_id"]):
        raise HTTPException(status_code=403, detail="No autorizado para eliminar este producto")

    await db["products"].delete_one({"_id": ObjectId(product_id)})
    return {"message": "Producto eliminado"}