from fastapi import HTTPException, status

class PermissionExistException(HTTPException):
    """权限名存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="该权限已存在!",
        )
class PermissionNotExistException(HTTPException):
    """权限名不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="权限不存在!",
        )
# class AccessNotExistException(HTTPException):
#     """访问控制不存在"""

#     def __init__(self):
#         super().__init__(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="access is not exists!",
#         )