from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from modules.product_models import (
    ProductResponse,
    ProductRequest,
    BulkDeleteRequest,
    BulkUpdateRequest
)

from modules.status_response import StatusMessage
from services import product_service

app = FastAPI(
    title='SoftStack Stockroom',
    version='0.0.3',
    contact={
        "name": 'Nicole Duhan',
        "email": 'softstackstudios@gmail.com'
    },
    description='A cozy inventory system, made with intention and clean code.'
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_current_token(token: str = Depends(oauth2_scheme)) -> str:
    """Dependency that extracts and verifies the bearer token."""
    valid = product_service.verify_token(token)
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


# ==============================
# AUTHENTICATION PORTAL
# ==============================

@app.post("/auth/token", tags=["Authentication"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Sign-in portal to acquire an authentication token."""
    token = product_service.authenticate_user(form_data.username, form_data.password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": token, "token_type": "bearer"}


# ==============================
# PRODUCT MANAGEMENT ENDPOINTS
# ==============================

@app.get("/products", response_model=List[ProductResponse], tags=["Products"])
def get_products(
        limit: int = 20,
        offset: int = 0,
        token: str = Depends(get_current_token)
):
    """Fetch paginated products."""
    return product_service.get_products_paginated(limit=limit, offset=offset)


@app.get("/product/{product_id}", response_model=ProductResponse, tags=["Products"])
def get_product(product_id: int, token: str = Depends(get_current_token)):
    """Fetch a single product by ID."""
    product = product_service.get_product_by_id(product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} was not found."
        )
    return product


@app.get("/products/price", response_model=List[ProductResponse], tags=["Products"])
def get_all_products_price_range(
        min_price: float,
        max_price: float,
        token: str = Depends(get_current_token)
):
    """Fetch products within a specific price range."""
    if min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price cannot be greater than max_price."
        )
    return product_service.get_products_by_price_range(min_price, max_price)


@app.get("/products/search", response_model=List[ProductResponse], tags=["Products"])
def search_products(
        product_price: float,
        product_type: Optional[str] = None,
        token: str = Depends(get_current_token)
):
    """Search products by target price and optional category type."""
    return product_service.search_products(product_price, product_type)


@app.post("/products/mod", response_model=StatusMessage, tags=["Products"])
def update_products(
        product: ProductRequest,
        token: str = Depends(get_current_token)
):
    """Add a new product or update an existing one."""
    if not product.Name.strip() or not product.Type.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product name and type cannot be empty."
        )

    if product.ID:
        existing_product = product_service.get_product_by_id(product.ID)
        if existing_product:
            product_service.update_existing_product(product)
            return StatusMessage(content="Product has been successfully modified!")

    product_service.add_new_product(product)
    return StatusMessage(content="Product has been successfully added!")


# ==============================
# BULK OPERATIONS
# ==============================

@app.delete("/products/bulk-delete", tags=["Bulk Operations"])
def delete_products(
        payload: BulkDeleteRequest,
        token: str = Depends(get_current_token)
):
    """Delete multiple products by passing a list of IDs."""
    product_service.bulk_delete_products(payload.product_ids)
    return StatusMessage(content=f"Successfully deleted {len(payload.product_ids)} items.")


@app.post("/products/bulk-save", response_model=StatusMessage, tags=["Bulk Operations"])
def bulk_save_products(
        payload: BulkUpdateRequest,
        token: str = Depends(get_current_token)
):
    """Add or update multiple products in a single request."""
    product_service.bulk_save_products(payload.products)
    return StatusMessage(content=f"Successfully processed {len(payload.products)} products.")


""" Thanks for using SoftStack Studios! """
