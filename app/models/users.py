from pydantic import BaseModel, Field
from typing import Optional

# creamos el modelo de nuestro usuario

class User(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id") 
    usuario: str
    email: str
    carrito: str


    class Config:
        # Esto permite que MongoDB's '_id' se mapee a 'id' en tu modelo
        populate_by_name = True 