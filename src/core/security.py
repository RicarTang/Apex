from typing import Union
from datetime import timedelta, datetime
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends, Request
from fastapi.exceptions import HTTPException
from tortoise.queryset import QuerySet
from ..db.models import Users
from ..utils.log_util import log
import config



oauth2_bearer = HTTPBearer()


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
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    log.debug(f"encoded_jwt:{encoded_jwt}")
    return encoded_jwt


async def check_jwt_auth(
    request: Request, bearer: HTTPAuthorizationCredentials = Depends(oauth2_bearer)
) -> QuerySet:
    """校验JWT,return当前用户

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
        payload = jwt.decode(bearer.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        log.error("JWT校验错误！")
        raise credentials_exception

    user = await Users.get(username=username)
    log.debug(f"当前用户：{user}")
    return user
