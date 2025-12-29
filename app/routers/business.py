from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas.users import UserCreate, UserLogin, UserResponse
from ..core.auth import Hash, get_current_user,create_access_token
from typing import List
from app.database import get_db


router = APIRouter(
    prefix="/business",
    tags=["business"],
    responses={status.HTTP_404_NOT_FOUND: {"message":"No encontrado"}}
)