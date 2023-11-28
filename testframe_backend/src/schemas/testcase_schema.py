from typing import Optional, List
from pydantic import BaseModel, Field
from ..db.enum import BoolEnum, ApiMethodEnum, RequestParamTypeEnum
from ..db.models import Testcase_Pydantic
from .common_schema import PageParam


class TestCaseIn(BaseModel):
    """测试用例 request schema"""

    case_no: str = Field(max_length=10, description="用例编号")
    case_title: str = Field(max_length=50, description="用例名称/标题")
    case_description: Optional[str] = Field(max_length=100, description="用例说明")
    case_module: str = Field(max_length=20, description="用例所属模块")
    case_sub_module: Optional[str] = Field(max_length=20, description="用例子模块")
    case_is_execute: BoolEnum = Field(
        default=BoolEnum.TRUE, description="用例是否执行;1: True, 0: False"
    )
    api_path: str = Field(description="用例接口地址path")
    api_method: ApiMethodEnum = Field(default=ApiMethodEnum.GET, description="api请求方法")
    request_headers: Optional[dict] = Field(description="请求头")
    request_param_type: RequestParamTypeEnum = Field(
        default=RequestParamTypeEnum.BODY,
        description="请求参数类型;body: json类型;query: 查询参数;path: 路径参数",
    )
    request_param: str = Field(description="请求参数")
    expect_code: int = Field(description="预期网络状态码")
    expect_result: Optional[str] = Field(description="预期结果")
    expect_data: Optional[str] = Field(description="预期返回数据")
    request_to_redis: BoolEnum = Field(
        default=BoolEnum.FALSE, description="是否保存请求体到redis;1: True, 0: False"
    )
    response_to_redis: BoolEnum = Field(
        default=BoolEnum.FALSE, description="是否保存响应体到redis;1: True, 0: False"
    )
    case_editor: Optional[str] = Field(description="用例编写者")
    remark: Optional[str] = Field(description="备注")


class TestCaseTo(Testcase_Pydantic):
    """测试用例 response schema"""

    pass


# class TestCases(List[TestCaseTo]):
#     pass


class TestCasesTo(PageParam):
    """翻页测试用例 response schema"""

    data: List[Testcase_Pydantic]


class ExecuteTestcaseIn(BaseModel):
    """执行单条测试用例request schema"""

    case_id: int
