from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr


class BrandBase(BaseModel):
    name: constr(min_length=3, max_length=255)


class ProductBase(BaseModel):
    name: constr(min_length=3, max_length=255)
    sku: constr(min_length=4, max_length=255)
    price: float
    brand_id: str


class ProductReturn(ProductBase):
    id: int
    create_by: str
    update_by: str

    class Config:
        orm_mode = True


class BrandReturn(BrandBase):
    id: int

    class Config:
        orm_mode = True
