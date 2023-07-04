"""认证相关"""
from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    UnauthenticatedUser,
    AuthenticationError,
    SimpleUser
)
from jose import JWTError, jwt




oauth2_bearer = HTTPBearer()
# jwt相关配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30



