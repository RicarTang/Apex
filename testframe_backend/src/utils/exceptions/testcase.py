from typing import Any
from fastapi import HTTPException, status


class TestcaseNotExistException(HTTPException):
    """测试用例不存在"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Testcase does not exist!",
        )


class RequestTimeOutException(HTTPException):
    """用例执行请求超时"""

    def __init__(self):
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request time out!",
        )


class AssertErrorException(HTTPException):
    """用例断言错误"""

    def __init__(self, detail: Any,result: Any):
        self.detail = detail
        self.result = result
        super().__init__(
            status_code=status.HTTP_417_EXPECTATION_FAILED,
            detail=self.detail,
        )
