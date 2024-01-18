from fastapi import HTTPException, status


class TestEnvNotExistException(HTTPException):
    """测试环境不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Environment does not exist!",
        )
class CurrentTestEnvNotSetException(HTTPException):
    """未设置当前环境"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current environment is not set!",
        )