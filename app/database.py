from motor.motor_asyncio import AsyncIOMotorClient
import os 
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("MONGODB_URL")


# client = AsyncIOMotorClient(URL)
# database = client.ecommerce

# def get_db():
#     """Retorna la base de datos para usar en dependencias"""
#     return database

async def get_db():
    client = AsyncIOMotorClient(URL)
    db = client.ecommerce
    try:
        yield db
    finally:
        client.close()

