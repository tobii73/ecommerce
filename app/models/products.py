from pydantic import BaseModel, Field
from typing import Optional

# creamos el modelo de nuestro producto

class Product(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id") 
    nombre: str
    precio: float
    stock: int

    class Config:
        # Esto permite que MongoDB's '_id' se mapee a 'id' en tu modelo
        populate_by_name = True 