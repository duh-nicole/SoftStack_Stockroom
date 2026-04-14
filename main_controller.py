from fastapi import FastAPI, HTTPException, status
from typing import List, Optional
from modules.product_models import Products, ProductsRequest
from modules.status_response import StatusMessage
from services import game_service

app = FastAPI(title='Module 6 API',
              version='0.0.3',
              contact={"name": 'Nicole Duhan', "email": 'nduhan@mail.mccneb.edu'},
              description ='Assignment 6')

@app.get("/products", response_model=List[Products], responses={400: {"model": StatusMessage}})
async def get_products():
    games = await game_service.get_all_games()
    if not games:
        raise HTTPException(status_code=400, detail="No entries exist!")
    return games

@app.get("/product/{product_id}", response_model=Products, responses={400: {"model": StatusMessage}})
async def get_product(product_id: int):
    game = await game_service.get_game_by_id(product_id)
    if not game:
        raise HTTPException(status_code=400, detail="No entry was found matching your query.")
    return game

@app.get("/products/price", response_model=List[Products], responses={400: {"model": StatusMessage}})
async def get_all_products_price_range(min_price: float, max_price: float):
    results = await game_service.get_games_by_price_range(min_price, max_price)
    if not results:
        raise HTTPException(status_code=400, detail="No products were found matching your criteria!")
    return results

@app.get("/products/search", response_model=List[Products], responses={400: {"model": StatusMessage}})
async def search_products(product_price: float, product_type: Optional[str] = None):
    results = await game_service.search_games(product_price, product_type)
    if not results:
        raise HTTPException(status_code=400, detail="No products were found from the price or type given!")
    return results

@app.post("/products/mod", responses={400: {"model": StatusMessage}})
async def update_products(products: ProductsRequest):
    ## Checking if required strings are empty
    if products.Name == "" or products.Type == "":
        raise HTTPException(status_code=400, detail="The Request Object was not sent properly!")
    existing_game = await game_service.get_game_by_id(products.ID)
    if existing_game:
        await game_service.update_existing_game(products)
        return "Modified Product!"
    else:
        await game_service.add_new_game(products)
        return "Added New Product!"

