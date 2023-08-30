from typing import Optional, TypeVar, Generic
from pydantic import Field, BaseModel
from pydantic.generics import GenericModel


DataT = TypeVar("DataT")


class ResultResponse(GenericModel, Generic[DataT]):
    """
    自定义返回模型，使用 generic-models 定义自定义模型
    https://pydantic-docs.helpmanual.io/usage/models/#generic-models
    所有返回数据都用如下格式，方便前端统一处理
    {
        code: 200,
        message: 'success',
        result: None
    }
    """

    code: int = Field(default=200, description="返回码")
    message: str = Field(default="success", description="消息内容")
    result: Optional[DataT] = Field(description="返回数据主体")


class PageParam(BaseModel):
    """翻页接口参数"""

    page: int
    limit: int
    total: int
