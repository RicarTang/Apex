from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from ..db.enum import BoolEnum, ApiMethodEnum, RequestParamTypeEnum
from .common import PageParam, DefaultModel


class TestCaseIn(BaseModel):
    """测试用例 request schema"""

    case_no: str = Field(max_length=10, description="用例编号", alias="caseNo")
    case_title: str = Field(max_length=50, description="用例名称/标题", alias="caseTitle")
    case_description: Optional[str] = Field(
        default=None, max_length=100, description="用例说明", alias="caseDescription"
    )
    case_module: str = Field(max_length=20, description="用例所属模块", alias="caseModule")
    case_sub_module: Optional[str] = Field(
        default=None, max_length=20, description="用例子模块", alias="caseSubModule"
    )
    case_is_execute: Optional[BoolEnum] = Field(
        default=BoolEnum.TRUE,
        description="用例是否执行;1: True, 0: False",
        alias="caseIsExecute",
    )
    api_path: str = Field(description="用例接口地址path", alias="apiPath")
    api_method: Optional[ApiMethodEnum] = Field(
        default=ApiMethodEnum.GET, description="api请求方法", alias="apiMethod"
    )
    request_headers: Optional[dict] = Field(
        default=None, description="请求头", alias="requestHeaders"
    )
    request_param_type: Optional[RequestParamTypeEnum] = Field(
        default=RequestParamTypeEnum.BODY,
        description="请求参数类型;body: json类型;query: 查询参数;path: 路径参数",
        alias="requestParamType",
    )
    request_param: str = Field(description="请求参数", alias="requestParam")
    expect_code: int = Field(description="预期网络状态码", alias="expectCode")
    expect_result: Optional[str] = Field(
        default=None, description="预期结果", alias="expectResult"
    )
    expect_data: Optional[str] = Field(
        default=None, escription="预期返回数据", alias="expectData"
    )
    request_to_redis: Optional[BoolEnum] = Field(
        default=BoolEnum.FALSE,
        description="是否保存请求体到redis;1: True, 0: False",
        alias="requestToRedis",
    )
    response_to_redis: Optional[BoolEnum] = Field(
        default=BoolEnum.FALSE,
        description="是否保存响应体到redis;1: True, 0: False",
        alias="responseToRedis",
    )
    case_editor: Optional[str] = Field(
        default=None, description="用例编写者", alias="caseEditor"
    )
    remark: Optional[str] = Field(default=None, description="备注")


class TestCaseTo(DefaultModel):
    """测试用例 response schema"""

    model_config = ConfigDict(from_attributes=True)
    case_no: Optional[str] = Field(
        default=None, description="用例编号", serialization_alias="caseNo"
    )
    case_title: Optional[str] = Field(
        default=None, description="用例名称/标题", serialization_alias="caseTitle"
    )
    case_description: Optional[str] = Field(
        default=None, description="用例说明", serialization_alias="caseDescription"
    )
    case_module: Optional[str] = Field(
        default=None, description="用例所属模块", serialization_alias="caseModule"
    )
    case_sub_module: Optional[str] = Field(
        default=None, description="用例子模块", serialization_alias="caseSubModule"
    )
    case_is_execute: Optional[BoolEnum] = Field(
        default=None,
        description="用例是否执行;1: True, 0: False",
        serialization_alias="caseIsExecute",
    )
    api_path: Optional[str] = Field(
        default=None, description="用例接口地址path", serialization_alias="apiPath"
    )
    api_method: Optional[ApiMethodEnum] = Field(
        default=None,
        description="api请求方法",
        serialization_alias="apiMethod",
    )
    request_headers: Optional[dict] = Field(
        default=None, description="请求头", serialization_alias="requestHeaders"
    )
    request_param_type: Optional[RequestParamTypeEnum] = Field(
        default=None,
        description="请求参数类型;body: json类型;query: 查询参数;path: 路径参数",
        serialization_alias="requestParamType",
    )
    request_param: Optional[str] = Field(
        default=None, description="请求参数", serialization_alias="requestParam"
    )
    expect_code: Optional[int] = Field(
        default=None, description="预期网络状态码", serialization_alias="expectCode"
    )
    expect_result: Optional[str] = Field(
        default=None, description="预期结果", serialization_alias="expectResult"
    )
    expect_data: Optional[str] = Field(
        default=None, description="预期返回数据", serialization_alias="expectData"
    )
    request_to_redis: Optional[BoolEnum] = Field(
        default=None,
        description="是否保存请求体到redis;1: True, 0: False",
        serialization_alias="requestToRedis",
    )
    response_to_redis: Optional[BoolEnum] = Field(
        default=None,
        description="是否保存响应体到redis;1: True, 0: False",
        serialization_alias="responseToRedis",
    )
    case_editor: Optional[str] = Field(
        default=None, description="用例编写者", serialization_alias="caseEditor"
    )
    remark: Optional[str] = Field(default=None, description="备注")


# class TestCases(List[TestCaseTo]):
#     pass


class TestCasesTo(PageParam):
    """翻页测试用例 response schema"""

    data: List[TestCaseTo]


class ExecuteTestcaseIn(BaseModel):
    """执行单条测试用例request schema"""

    case_id: int


class DeleteCaseIn(BaseModel):
    """删除用例schema"""

    case_ids: List[int] = Field(alias="caseIds")


class UpdateCaseIn(BaseModel):
    """更新用例schema"""

    case_no: Optional[str] = Field(
        default=None, max_length=10, description="用例编号", alias="caseNo"
    )
    case_title: Optional[str] = Field(
        default=None, max_length=50, description="用例名称/标题", alias="caseTitle"
    )
    case_description: Optional[str] = Field(
        default=None, max_length=100, description="用例说明", alias="caseDescription"
    )
    case_module: Optional[str] = Field(
        default=None, max_length=20, description="用例所属模块", alias="caseModule"
    )
    case_sub_module: Optional[str] = Field(
        default=None, max_length=20, description="用例子模块", alias="caseSubModule"
    )
    case_is_execute: Optional[BoolEnum] = Field(
        default=None,
        description="用例是否执行;1: True, 0: False",
        alias="caseIsExecute",
    )
    api_path: Optional[str] = Field(
        default=None, description="用例接口地址path", alias="apiPath"
    )
    api_method: Optional[ApiMethodEnum] = Field(
        default=None, description="api请求方法", alias="apiMethod"
    )
    request_headers: Optional[dict] = Field(
        default=None, description="请求头", alias="requestHeaders"
    )
    request_param_type: Optional[RequestParamTypeEnum] = Field(
        default=None,
        description="请求参数类型;body: json类型;query: 查询参数;path: 路径参数",
        alias="requestParamType",
    )
    request_param: Optional[str] = Field(
        default=None, description="请求参数", alias="requestParam"
    )
    expect_code: Optional[int] = Field(
        default=None, description="预期网络状态码", alias="expectCode"
    )
    expect_result: Optional[str] = Field(
        default=None, description="预期结果", alias="expectResult"
    )
    expect_data: Optional[str] = Field(
        default=None, escription="预期返回数据", alias="expectData"
    )
    request_to_redis: Optional[BoolEnum] = Field(
        default=None,
        description="是否保存请求体到redis;1: True, 0: False",
        alias="requestToRedis",
    )
    response_to_redis: Optional[BoolEnum] = Field(
        default=None,
        description="是否保存响应体到redis;1: True, 0: False",
        alias="responseToRedis",
    )
    case_editor: Optional[str] = Field(
        default=None, description="用例编写者", alias="caseEditor"
    )
    remark: Optional[str] = Field(default=None, description="备注")
