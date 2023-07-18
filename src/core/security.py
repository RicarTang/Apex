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
from ..crud import UsersCrud


oauth2_bearer = HTTPBearer(auto_error=False)


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
        expire = datetime.utcnow() + timedelta(
            minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    log.debug(f"encoded_jwt:{encoded_jwt}")
    return encoded_jwt


async def check_jwt_auth(
    request: Request, bearer: HTTPAuthorizationCredentials = Depends(oauth2_bearer)
) -> QuerySet:
    """校验JWT,return当前用户

    Args:
        request (Request): Request对象
        bearer (HTTPAuthorizationCredentials, optional): _description_. Defaults to Depends(oauth2_bearer).

    Raises:
        unauthorized_exception: _description_
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
    unauthorized_exception = HTTPException(
        status_code=401,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
    # 首次创建用户跳过认证
    is_first_user = await Users.all().exists()
    print(request.body)
    if request.url.path == "/user/create" and (is_first_user is False):
        # 创建第一个用户，直接放行
        await UsersCrud.create_superadmin(request.body)
    try:
        # decode校验
        payload = jwt.decode(
            bearer.credentials, config.SECRET_KEY, algorithms=[config.ALGORITHM]
        )
    except AttributeError:
        raise unauthorized_exception
    except JWTError:
        raise credentials_exception
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception

    user = await Users.get(username=username)
    # 保存用户到request
    request.state.user = user
    log.debug(f"当前用户：{user}")
    return user
