from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
from modules.product_models import Products, ProductsRequest
from modules.status_response import StatusMessage
from services import game_service

app = FastAPI(title='Module 6 API',
              version='0.0.3',
              contact={"name": 'Nicole Duhan', "email": 'nduhan@mail.mccneb.edu'},
              description ='Assignment 6')

@app.get("/products", response_model=List[Products])
async def get_products():
    return await game_service.get_all_games()

@app.get("/product/{product_id}", response_model=Products)
async def get_product(product_id: int):
    game = await game_service.get_game_by_id(product_id)
    return game

## Search Endpoints ##
@app.get("/products/price", response_model=List[Products])
async def get_all_products_price_range(min_price: float, max_price: float):
    return await game_service.get_games_by_price_range(min_price, max_price)

@app.get("/products/search", response_model=List[Products])
async def search_products(product_price: float, product_type: Optional[str] = None):
    return await game_service.search_games(product_price, product_type)

@app.post("/products/mod")
async def update_products(products: ProductsRequest):
    existing_game = await game_service.get_game_by_id(products.ID)

    if existing_game:
        await game_service.update_existing_game(products)
        return "Modified Product!"
    else:
        await game_service.add_new_game(products)
        return "Added New Product!"

