from pydantic import BaseModel,  Field, field_validator
from typing import Optional
from datetime import datetime

###########---PRODUCTS SCHEMAS---###########

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    category: Optional[str] = Field(None, max_length=50)

    @field_validator('name')
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        """Valida que el nombre no sea solo espacios"""
        if v.strip() == "":
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()  # También limpia espacios extra
    
class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None


class ProductResponse(ProductCreate):
    id: str = Field(alias="_id")
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        populate_by_name = True