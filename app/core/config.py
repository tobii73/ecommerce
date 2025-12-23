from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv

load_dotenv(".env")
class Settings(BaseSettings):
    # MongoDB
    MONGODB_URL: str = "mongodb+srv://ecommerce_db:Lo5AlE48b7edwKsd@ecommerce.wquxnfz.mongodb.net/?appName=Ecommerce"
    DATABASE_NAME: str = "ecommerce"
    
    # JWT
    key = os.getenv("KEY")
    JWT_SECRET_KEY: str = key
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

settings = Settings()