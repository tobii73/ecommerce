from pydantic import BaseModel, EmailStr, Field
from typing import Optional

###########---USER SCHEMAS---###########

#Creando al nuevo usuario
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str  # Esta se hasheará antes de guardarse

#Login
class UserLogin(BaseModel):
    username: str
    password: str

# Esquema para devolver datos 
class UserResponse(BaseModel):
    id: str = Field(alias="_id") 
    username: str
    email: EmailStr
    
    
    class Config:
        populate_by_name = True


###########---AUTH_USER SCHEMAS---###########
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str 