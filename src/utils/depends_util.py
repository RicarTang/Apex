from typing import Union
from jose import JWTError, jwt
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
from passlib.hash import md5_crypt
from fastapi import Depends
from fastapi.exceptions import HTTPException
from ..models import Users
from fastapi.encoders import jsonable_encoder

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await Users.get(username=username)
    if user is None:
        raise credentials_exception
    user_dict = jsonable_encoder(user[0])
    user_dict["access_token"] = token
    return user_dict


def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    """
    创建token Depends
    :param data:带有用户标识的键值对，sub为JWT的规范
    :param expires_delta:过期时间
    :return:
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# async def md5_crypt_hash(content: str):
#     """md5 hash加密."""
#     return md5_crypt.hash(content)
#
#
# async def md5_crypt_verify(content):
#     """md5 hash验证"""
