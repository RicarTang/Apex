"""认证相关"""
from fastapi import Request
from fastapi.security import HTTPBearer
from fastapi.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.authentication import (
    AuthenticationBackend,
    AuthCredentials,
    UnauthenticatedUser,
)
from jose import JWTError, jwt
from casbin import Enforcer
from casbin_tortoise_adapter import TortoiseAdapter


adapter = TortoiseAdapter()
# casbin实例
enforcer = Enforcer("rbac_model.conf", adapter)


oauth2_bearer = HTTPBearer()
# jwt相关配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


class JWTMiddleware(AuthenticationBackend):
    async def authenticate(self, request: Request):
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # 检查 JWT Token 是否存在并验证
        if "Authorization" not in request.headers:
            return
        # 在此处执行验证逻辑，例如使用 JWT 库验证 Token 的有效性
        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "bearer":
                return
            decoded = jwt.decode(credentials, SECRET_KEY, algorithms=[ALGORITHM])
            username = decoded.get("sub")
            if username is None:
                raise credentials_exception

        except (ValueError, UnicodeDecodeError, JWTError):
            raise credentials_exception


class JWTAuthenticationBackend(AuthenticationBackend):
    """验证JWT

    Args:
        AuthenticationBackend (_type_): 继承AuthenticationBackend
    """

    async def authenticate(self, request: Request):
        """验证用户

        Args:
            request (Request): Request对象

        Returns:
            _type_: _description_
        """
        credentials_exception = HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        # 从请求中获取 JWT 令牌并根据令牌验证用户身份
        if "Authorization" not in request.headers:
            return
        auth = request.headers["authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "bearer":
                return
            decoded = jwt.decode(credentials, SECRET_KEY, algorithms=[ALGORITHM])
            username = decoded.get("sub")
            if username is None:
                raise credentials_exception
        except (ValueError, UnicodeDecodeError, JWTError) as exc:
            raise credentials_exception

        # if user:
        #     return AuthCredentials(scopes=[user.role]), user

        # return AuthCredentials(), UnauthenticatedUser()
