from fastapi import HTTPException, status


class MenuNotExistException(HTTPException):
    """菜单不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu does not exist!",
        )
