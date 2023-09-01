from fastapi import HTTPException, status


class TestEnvNotExistException(HTTPException):
    """测试环境不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment does not exist!",
        )