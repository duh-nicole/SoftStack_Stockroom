from pydantic import BaseModel, Field
from typing import Optional


# Base class with shared fields
class ProductBase(BaseModel):
    Name: str = Field(...,
                      example = "Cozy Cinnamon Latte")
    Price: float = Field(...,
                         gt = 0,
                         example = 4.50)
    Type: str = Field(...,
                      example = "Beverage")


# Used when CREATING a new product (ID is optional or omitted if auto-incremented)
class ProductCreate(ProductBase):
    ID: Optional[int] = None


# Used when RETURNING a product from the DB (ID is guaranteed to exist)
class ProductResponse(ProductBase):
    ID: int

    class Config:
        from_attributes = True  # Allows Pydantic to read ORM / row dicts easily

