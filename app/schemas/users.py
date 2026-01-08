from pydantic import BaseModel, EmailStr,  Field, field_validator
from typing import Optional
from enum import Enum
import re

###########---USER ROLE---###########

class UserRole(str, Enum):
    CUSTOMER = "customer"      # Solo compra
    SELLER = "seller"          # Tiene negocio y vende

###########---USER SCHEMAS---###########

#Creando al nuevo usuario
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr  # Valida formato email automáticamente
    password: str = Field(..., min_length=8)

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Debe tener al menos una mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('Debe tener al menos una minúscula')
        if not re.search(r'\d', v):
            raise ValueError('Debe tener al menos un número')
        return v
    
    @field_validator('username')
    @classmethod
    def validate_username_format(cls, v: str) -> str:
        if not v.replace("_", "").isalnum():
            raise ValueError('Solo letras, números y guiones bajos (_)')
        if v.startswith('_') or v.endswith('_'):
            raise ValueError('No puede empezar o terminar con _')
        return v

#Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Esquema para devolver datos 
class UserResponse(BaseModel):
    id: str = Field(..., alias="_id")
    username: str
    email: EmailStr
    role: UserRole
    
    class Config:
        populate_by_name = True


###########---AUTH_USER SCHEMAS---###########
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str 