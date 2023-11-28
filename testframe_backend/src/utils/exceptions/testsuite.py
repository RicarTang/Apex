from fastapi import HTTPException, status


class TestsuiteNotExistException(HTTPException):
    """测试套件不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testsuite does not exist!",
        )
