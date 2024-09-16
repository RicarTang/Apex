from fastapi import HTTPException, status


class TokenExpiredException(HTTPException):
    """token已过期"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token已过期!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenUnauthorizedException(HTTPException):
    """token未认证"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未经过身份验证!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenInvalidException(HTTPException):
    """token无效"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token无效!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserLoggedOutException(HTTPException):
    """用户退出登录"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户已注销，请重新登录!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotExistException(HTTPException):
    """用户不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在!",
        )


class PasswordValidateErrorException(HTTPException):
    """密码验证错误"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="密码验证错误!",
        )


class UserUnavailableException(HTTPException):
    """用户状态不可用"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="用户状态为不可用!",
        )