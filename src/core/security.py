from typing import Union
from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi.security import HTTPBearer
from fastapi import Depends, Request
from config import config
from ..db.models import Users
from ..utils.log_util import log
from ..utils.exception_util import (
    TokenUnauthorizedException,
    TokenExpiredException,
    TokenInvalidException,
)
from ..crud import UsersCrud


oauth2_bearer = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    创建token

    Args:
        data (dict): 带有用户标识的键值对,sub为JWT的规范
        expires_delta (Union[timedelta, None], optional): 过期时间

    Returns:
        _type_: jwt token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    jwt_token = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    log.debug(f"encoded_jwt:{jwt_token}")
    return jwt_token


async def check_jwt_auth(
    request: Request, bearer: HTTPBearer = Depends(oauth2_bearer)
) -> Users:
    """校验JWT,return当前用户

    Args:
        request (Request): Request对象
        bearer (HTTPBearer): HTTPBearer

    Raises:
        TokenUnauthorizedException: token未认证
        TokenExpiredException: token已过期

    Returns:
        Users: 用户对象
    """
    try:
        # jwt decode,验证jwt
        payload = jwt.decode(
            bearer.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
    except AttributeError:
        raise TokenUnauthorizedException
    except JWTError:
        raise TokenExpiredException
    username: str = payload.get("sub")
    # 严格规定login接口传递的sub
    if not username:
        raise TokenInvalidException
    user = await Users.get(username=username)
    # 保存用户到request
    request.state.user = user
    log.debug(f"当前用户：{user}")
    return user
