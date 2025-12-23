from pydantic import BaseModel

# creamos el modelo de nuestro producto

class Product(BaseModel):
    id: str
    nombre: str
    precio: float
    categoria: list
    reviews: list
    stock: int