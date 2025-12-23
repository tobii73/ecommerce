from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
uri = "mongodb+srv://ecommerce_db:Lo5AlE48b7edwKsd@ecommerce.wquxnfz.mongodb.net/?appName=Ecommerce"
# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1')).ecommerce
# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

collecction = client.products

