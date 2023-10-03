from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr

from shared_package.db.enums import Rol


class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    is_active: bool = True
    password: constr(min_length=8, max_length=255)


class UserReturn(UserBase):
    id: int

    class Config:
        orm_mode = True


class UserBaseAdmin(UserBase):
    rol_type: Rol = Rol.user


class UserUpdate(BaseModel):
    full_name: Optional[str]
    email: Optional[EmailStr]
    is_active: Optional[bool]
    password: Optional[str]
    