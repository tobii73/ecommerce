from fastapi import FastAPI

app = FastAPI()

@app.get('/')
async def welcome():
    return {
        "message": "Bienvenido"
    }


@app.get('/api/productos')
async def get_products():
    return 'all products'

@app.post('/api/productos')
async def create_products():
    return 'create products'

@app.get('/api/productos/{id}')
async def get_products_id(id:str):
    return 'single products'

@app.put('/api/productos/{id}')
async def update_products(id : str):
    return 'update products'

@app.delete('/api/productos/{id}')
async def delete_products(id: str):
    return 'delete products'