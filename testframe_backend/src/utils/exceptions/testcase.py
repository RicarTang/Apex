from fastapi import HTTPException, status


class TestcaseNotExistException(HTTPException):
    """测试用例不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testcase does not exist!",
        )
