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

# Remove password from response
class UserResponse(BaseModel):
    type: str
    username: str
    email: str
    id: int
    uuid: str

class LoginBase(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    type: str
    username: str
    email: str
    id: int
    uuid: str

class AdminUserBase(BaseModel):
    username: str
    password: str
    email: str
    admin_status: Optional[str] = None

class AdminUserResponse(BaseModel):
    type: str
    username: str
    email: str
    id: int
    uuid: str
    admin_status: str

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    category_name: Optional[str] = None
    purchase_price: float
    restock_price: float
    currency: str
    quantity: int

class TransactionBase(BaseModel):
    product_id: int
    user_id: int
    currency: str
    quantity: int
    transaction_type: str