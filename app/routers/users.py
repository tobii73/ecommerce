from fastapi import APIRouter, status, HTTPException
from models.users import User
from database import client
from ..schemas.users import user_schema, usuarios_db
from dotenv import load_dotenv
import os
from bson import ObjectId
load_dotenv(".env")

key = os.getenv("KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 30

router = APIRouter(
    prefix="users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND: {"message":"No encontrado"}}
)


@router.get("/",response_model=list[User])
async def users():
    return usuarios_db(client.users.find())

@router.get("/{id}")
async def path_users():
    return search_user("_id", ObjectId(id))

@router.get("/query/") # Query , se utiliza para filtrar 
async def query_user(id : str):
    return search_user("_id", ObjectId(id))

@router.post("/", response_model=User,status_code=status.HTTP_201_CREATED)
async def user(user: User):
    
    if search_user_by_email("email",user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este email ya está registrado"
        )

    user_dict = user.model_dump(exclude_none=True)
    
    id = client.users.insert_one(user_dict).inserted_id

    new_user = user_schema(client.users.find_one({"_id": id}))
    
    return User(**new_user)


@router.put("/",response_model=User)
async def user(user: User):

    user_dict = dict(user)
    del user_dict["id"]

    try:
        client.users.find_one_and_replace(
            {"_id":ObjectId(user.id)}, user_dict)
    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se ha encontrado el usuario")
 
    return search_user("_id",ObjectId(user.id))

@router.delete("/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def user(id: str):
   
    found =  client.users.find_one_and_delete({"_id":ObjectId(id)})

    if not found:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se ha encontrado el usuario")
    


def search_user(field:str, key) -> bool:
    try:
        user = client.users.find_one({field:key})
        return User(**user_schema(user)) is not None
    except:
        return False
    
def search_user_by_email(field:str, key) -> bool:
    try:
       user = client.users.find_one({field:key})
       return User(**user_schema(user)) is not None
    except:
        return False


