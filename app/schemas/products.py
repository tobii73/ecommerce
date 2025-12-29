from pydantic import BaseModel, Field
from typing import Optional

###########---PRODUCTS SCHEMAS---###########

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    category : Optional[str] = None
    price: float
    business_id: str  # Referencia al negocio que lo crea

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


class ProductResponse(ProductCreate):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True