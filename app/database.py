from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os 
from dotenv import load_dotenv

load_dotenv()


URL = os.getenv("MONGODB_URL")

url = URL
# Create a new client and connect to the server
client = MongoClient(url, server_api=ServerApi('1')).ecommerce
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

    
