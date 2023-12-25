from fastapi import HTTPException, status

class PermissionExistException(HTTPException):
    """权限名存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="this permission already exists!",
        )
class PermissionNotExistException(HTTPException):
    """权限名不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="permission is not exists!",
        )
class AccessNotExistException(HTTPException):
    """访问控制不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="access is not exists!",
        )