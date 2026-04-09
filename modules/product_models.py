from pydantic import BaseModel

class Products(BaseModel):
    ID: int
    Name: str
    Price: float
    Type: str

class ProductsRequest(BaseModel):
    ID: int
    Name: str
    Price: float
    Type: str

