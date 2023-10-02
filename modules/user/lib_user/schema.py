from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    is_active: bool = True
    is_admin: bool = False
    password: constr(min_length=8, max_length=255)


class UserReturn(UserBase):
    id: int

    class Config:
        orm_mode = True
