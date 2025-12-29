from motor.motor_asyncio import AsyncIOMotorClient
import os 
from dotenv import load_dotenv

load_dotenv()

URL = os.getenv("MONGODB_URL")


client = AsyncIOMotorClient(URL)
database = client.ecommerce 

def get_db():
    """Retorna la base de datos para usar en dependencias"""
    return database

# Función asíncrona para verificar conexión
async def test_connection():
    try:
        await client.admin.command('ping')
        print("✅ Pinged your deployment. You successfully connected to MongoDB with Motor!")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
