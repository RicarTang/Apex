from pydantic import BaseModel, Field
from .models import User_Pydantic
from typing import List,Optional


class Status(BaseModel):
    message: str


class UserIn(BaseModel):
    username: str
    surname: Optional[str]
    name: Optional[str]
    password: str = Field(min_length=6, max_length=20)
    descriptions: Optional[str] = Field(max_length=50)


class Users(BaseModel):
    result: List[User_Pydantic]
