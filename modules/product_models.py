from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional


class ProductBase(BaseModel):
    Name: str = Field(..., json_schema_extra={"example": "CodeLatte Mug"})
    Price: float = Field(..., gt=0, json_schema_extra={"example": 15.00})
    Type: str = Field(..., json_schema_extra={"example": "Merch"})
    DiscountPercent: float = Field(0.0, ge=0.0, le=100.0, description="Discount percentage (0-100)")


class ProductRequest(ProductBase):
    ID: Optional[int] = None


class ProductResponse(ProductBase):
    ID: int
    FinalPrice: float
    model_config = ConfigDict(from_attributes=True)


class BulkDeleteRequest(BaseModel):
    product_ids: List[int] = Field(..., min_length=1, json_schema_extra={"example": [1, 2, 3]})


class BulkUpdateRequest(BaseModel):
    products: List[ProductRequest] = Field(..., min_length=1)


""" Thanks for using SoftStack Studios! """

