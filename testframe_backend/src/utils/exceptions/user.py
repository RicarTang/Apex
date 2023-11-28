from fastapi import HTTPException, status


class TokenExpiredException(HTTPException):
    """token已过期"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenUnauthorizedException(HTTPException):
    """token未认证"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenInvalidException(HTTPException):
    """token无效"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserLoggedOutException(HTTPException):
    """用户退出登录"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User logged out, please log in again!",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotExistException(HTTPException):
    """用户不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail="User does not exist!",
        )


class PasswordValidateErrorException(HTTPException):
    """密码验证错误"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_200_OK,
            detail="Password validate error!",
        )


class UserUnavailableException(HTTPException):
    """用户状态不可用"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user status is unavailable!",
        )


class RoleNotExistException(HTTPException):
    """角色不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role does not exist!",
        )