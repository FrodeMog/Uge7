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