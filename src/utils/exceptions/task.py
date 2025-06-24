from fastapi import HTTPException, status


class TaskNotExistException(HTTPException):
    """task 不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="task不存在!",
        )
