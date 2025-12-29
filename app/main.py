from fastapi import FastAPI
from .routers import users, business, products

app = FastAPI()

app.include_router(users.router)
app.include_router(business.router)
app.include_router(products.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}