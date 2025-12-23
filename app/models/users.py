from pydantic import BaseModel

# creamos el modelo de nuestro usuario

class User(BaseModel):
    id: str
    usuario: str
    email: str
    carrito: list
    ordenes: list
    direcciones: list