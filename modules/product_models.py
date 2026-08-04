from pydantic import BaseModel, Field
from typing import List, Optional


class ProductBase(BaseModel):
    Name: str = Field(..., example="CodeLatte Mug")
    Price: float = Field(..., gt=0, example=15.00)
    Type: str = Field(..., example="Merch")
    DiscountPercent: float = Field(0.0, ge=0.0, le=100.0, description="Discount percentage (0-100)")


class ProductRequest(ProductBase):
    ID: Optional[int] = None


class ProductResponse(ProductBase):
    ID: int
    FinalPrice: float  # Dynamically calculated price after discount

    class Config:
        from_attributes = True


# Models for Bulk Operations
class BulkDeleteRequest(BaseModel):
    product_ids: List[int] = Field(..., min_items=1, example=[1, 2, 3])


class BulkUpdateRequest(BaseModel):
    products: List[ProductRequest] = Field(..., min_items=1)
