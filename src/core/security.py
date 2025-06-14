from typing import Union
from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi.security import HTTPBearer
from fastapi import Depends, Request
from src.config import config
from src.db.models import Users
from src.utils.log_util import log
from ..utils.exceptions.user import (
    TokenUnauthorizedException,
    TokenExpiredException,
    TokenInvalidException,
    UserLoggedOutException,
)
from ..services import UserService
from .redis import RedisService


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
    return jwt_token


async def check_jwt_auth(
    request: Request, bearer: HTTPBearer = Depends(oauth2_bearer)
) -> dict:
    """校验JWT

    Args:
        request (Request): Request对象
        bearer (HTTPBearer): HTTPBearer

    Raises:
        TokenUnauthorizedException: token未认证
        TokenExpiredException: token已过期
        TokenInvalidException: 无效token
        UserLoggedOutException: 用户退出登录

    Returns:
        dict : payload
    """
    try:
        # jwt decode,验证jwt
        payload = jwt.decode(
            # bearer.credentials 当前token，
            # config.SECRET_KEY 私钥，
            # algorithms hash算法
            bearer.credentials,
            config.SECRET_KEY,
            algorithms=[config.ALGORITHM],
        )
    except AttributeError:
        raise TokenUnauthorizedException
    except JWTError:
        raise TokenExpiredException
    # 查询token黑名单列表
    token_black_list = await RedisService().aioredis_pool.lrange(
        payload.get("sub") + "-token-blacklist", 0, -1
    )
    # 判断token是否在黑名单中
    if bearer.credentials in token_black_list:
        raise UserLoggedOutException
    return payload


async def get_current_user(
    request: Request, payload: dict = Depends(check_jwt_auth)
) -> Users:
    """获取当前登录用户

    Args:
        request (Request): _description_
        payload (dict): 一个字典
            example:{"sub":"tang","exp":30}

    Raises:
        TokenInvalidException: _description_

    Returns:
        Users: _description_
    """
    username: str = payload.get("sub")
    # 严格规定login接口传递的sub
    if not username:
        raise TokenInvalidException
    # 查询用户
    user = await UserService.query_user_by_username(username=username)
    return user
