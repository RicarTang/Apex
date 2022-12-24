from pydantic import BaseModel, Field
from .models import User_Pydantic
from typing import List


class Status(BaseModel):
    message: str


class UserIn(BaseModel):
    username: str
    surname: str
    name: str
    password: str = Field(min_length=6, max_length=20)
    descriptions: str = Field(max_length=50)


class Users(BaseModel):
    result: List[User_Pydantic]
