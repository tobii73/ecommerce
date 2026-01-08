from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

###########---BUSINESS SCHEMAS---###########

# Esquema base con campos comunes para un negocio
class BusinessBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None

# Esquema para la creación (POST /business/add)
class BusinessCreate(BusinessBase):
    # En un sistema con JWT, el dueño suele extraerse del token, 
    # pero puede definirse aquí si se envía manualmente.
    pass

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

# Esquema para las respuestas de la API (GET /business/get)
class BusinessResponse(BusinessBase):
    # Mapeamos el ID de MongoDB para que sea legible como string
    id: str = Field(alias="_id")
    name: str
    description: str
    owner_id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None 

    class Config:
        # Permite que Pydantic trabaje con los diccionarios de MongoDB
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "id": "60d5ecb8b39d1c3a2c8e4e1b",
                "name": "Mi Tienda Tech",
                "description": "Venta de periféricos",
                "category": "Electrónica",
                "owner_id": "60d5ec72b39d1c3a2c8e4e1a"
            }
        }


# Esquema para la eliminación (DELETE /business/delete)
class BusinessDelete(BaseModel):
    id: str = Field(alias="_id")