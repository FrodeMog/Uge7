from pydantic import BaseModel
from typing import Optional

class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    parent_name: Optional[str] = None

class UserBase(BaseModel):
    username: str
    password: str
    email: str

class AdminUserBase(BaseModel):
    username: str
    password: str
    email: str
    admin_status: Optional[str] = None

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    purchase_price: float
    restock_price: float
    currency: str
    quantity: int