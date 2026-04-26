from fastapi import FastAPI, HTTPException,status, Header
from typing import List, Optional
from modules.product_models import Products, ProductsRequest
from modules.status_response import StatusMessage
from services import game_service
from services.game_service import verify_token


app = FastAPI(title='Module 8 API',
              version='0.0.3',
              contact={"name": 'Nicole Duhan', "email": 'nduhan@mail.mccneb.edu'},
              description ='Assignment 8')

@app.get("/products", response_model=List[Products], responses={400: {"model": StatusMessage}, 401: {"model": StatusMessage}})
async def get_products(authorization: str = Header(None)):
    if not await verify_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token!")
    games = await game_service.get_all_games()
    if not games:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=StatusMessage(content="No entries exist!").dict())
    return games

@app.get("/product/{product_id}", response_model=Products, responses={400: {"model": StatusMessage}, 401: {"model": StatusMessage}})
async def get_product(product_id: int, authorization: str = Header(None)):
    if not await verify_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token!")
    game = await game_service.get_game_by_id(product_id)
    if not game:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=StatusMessage(content="Whoops! The product_id was not found.").dict())
    return game

@app.get("/products/price", response_model=List[Products], responses={400: {"model": StatusMessage}, 401: {"model": StatusMessage}})
async def get_all_products_price_range(min_price: float, max_price: float, authorization: str = Header(None)):
    if not await verify_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token!")
    results = await game_service.get_games_by_price_range(min_price, max_price)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=StatusMessage(content="Whoops! No products within the specified range.").dict())
    return results

@app.get("/products/search", response_model=List[Products], responses={400: {"model": StatusMessage}, 401: {"model": StatusMessage}})
async def search_products(product_price: float, product_type: Optional[str] = None, authorization: str = Header(None)):
    if not await verify_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token!")
    results = await game_service.search_games(product_price, product_type)
    if not results:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=StatusMessage(content="Whoops! No games meet your type and price.").dict())
    return results

@app.post("/products/mod", responses={400: {"model": StatusMessage}, 401: {"model": StatusMessage}})
async def update_products(products: ProductsRequest, authorization : str = Header(None)):
    if not await verify_token(authorization):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing token!")
    ## Checking if required strings are empty
    if products.Name == "" or products.Type == "":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=StatusMessage(content="Product type or name cannot be left empty!").dict())
    existing_game = await game_service.get_game_by_id(products.ID)
    if existing_game:
        await game_service.update_existing_game(products)
        return "Product has been successfully modified!"
    else:
        await game_service.add_new_game(products)
        return "Product has been successfully added!"

