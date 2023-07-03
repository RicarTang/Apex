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
from casbin import Enforcer
from casbin_tortoise_adapter import TortoiseAdapter


adapter = TortoiseAdapter()
# # casbin实例
# enforcer = Enforcer("rbac_model.conf", adapter)
enforcer = Enforcer("casbin/rbac_model.conf", "casbin/rbac_policy.csv")


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
    """验证JWT"""

    async def authenticate(self, request: Request):
        """重写authenticate

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
        print(request.scope)
        print(1)
        if "Authorization" not in request.headers:
            return None

        auth = request.headers["Authorization"]
        try:
            scheme, credentials = auth.split()
            if scheme.lower() != "bearer":
                return
            decoded = jwt.decode(credentials, SECRET_KEY, algorithms=[ALGORITHM])
        except (ValueError, UnicodeDecodeError, JWTError):
            raise AuthenticationError("Invalid basic auth credentials")
        username = decoded.get("sub")
        print(3)
        return AuthCredentials(["authenticated"]), SimpleUser(username)


