from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, EmailStr, constr


class Credentials(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=255)


class AuthReturn(BaseModel):
    access_token: str
    full_name: str
    expires_at: str
    rol_type: str
    uuid: str
    id: int
