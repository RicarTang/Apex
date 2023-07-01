"""安全权限模块"""
from typing import Union
from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# from passlib.hash import md5_crypt
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from tortoise.queryset import QuerySet
from ..db.models import Users

# from .. import schemas
# from fastapi.encoders import jsonable_encoder
from ..utils.log_util import log


# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
oauth2_bearer = HTTPBearer()
# jwt相关配置
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    创建token Depends
    :param data:带有用户标识的键值对，sub为JWT的规范
    :param expires_delta:过期时间
    :return: jwt
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    log.debug(f"encoded_jwt:{encoded_jwt}")
    return encoded_jwt


async def get_current_user(
    request: Request, bearer: HTTPAuthorizationCredentials = Depends(oauth2_bearer)
) -> QuerySet:
    """校验token,得到当前用户

    Args:
        request (Request): Requeset对象

    Raises:
        credentials_exception: _description_
        credentials_exception: _description_

    Returns:
        QuerySet: tortoise QuerySet对象
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # decode校验
        payload = jwt.decode(bearer.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        print("JWTError")
        raise credentials_exception

    user = await Users.get(username=username)
    log.debug(f"当前用户：{user}")
    return user


# def get_current_active_user(current_user:schemas.User=Depends(get_current_user)):
#     """获取当前活动用户"""
#     print("get_current_active_user")
#     if current_user.disabled:
#         raise HTTPException(status_code=400, detail="Inactive user")
#     return current_user


# async def md5_crypt_hash(content: str):
#     """md5 hash加密."""
#     return md5_crypt.hash(content)
#
#
# async def md5_crypt_verify(content):
#     """md5 hash验证"""
