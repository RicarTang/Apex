from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator
from ..db.models import TestsuitePydantic, TestSuiteTaskId
from .common import PageParam
from .testcase import TestCaseTo
from ..utils.log_util import log


class TestSuiteIn(BaseModel):
    """添加测试套件request schema"""

    suite_no: str = Field(max_length=10, description="套件编号")
    suite_title: str = Field(max_length=50, description="套件名称/标题")
    remark: Optional[str] = Field(description="备注")
    testcase_id: Optional[List[int]] = Field(
        gt=0, description="测试用例id", alias="testcase_id_list"
    )


class TestSuiteTo(TestsuitePydantic):
    """测试套件response schema"""

    testcases: List[TestCaseTo] = Field(description="套件包含的用例")
    task_id: Optional[str] = Field(description="运行测试的task id")

    @field_validator("task_id", mode="before")
    @classmethod
    def modify_task_id_before_validation(
        cls, value: Union[TestSuiteTaskId, None]
    ) -> Union[str, None]:
        """模型验证前修改入参

        Args:
            value (TestSuiteTaskId): TestSuiteTaskId orm对象

        Returns:
            Union[str, None]: 返回task_id | None
        """
        try:
            return value.task_id
        except AttributeError:
            # orm对象返回空，不做处理
            pass


class TestSuitesTo(PageParam):
    """翻页测试套件 response schema"""

    data: List[TestSuiteTo]


class TestSuiteId(BaseModel):
    """suite id"""

    suite_id: int = Field(description="测试套件id")