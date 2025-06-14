"""公共schema"""

from typing import Optional, TypeVar, Generic
from datetime import datetime
from pydantic import Field, BaseModel, ConfigDict


DataT = TypeVar("DataT")


class ResultResponse(BaseModel, Generic[DataT]):
    """
    自定义返回模型，使用 generic-models 定义自定义模型
    https://pydantic-docs.helpmanual.io/usage/models/#generic-models
    所有返回数据都用如下格式，方便前端统一处理
    {
        success: True,  # 简化接口状态码
        message: 'success',
        result: None
    }
    """

    success: bool = Field(default=True, description="成功状态")
    message: str = Field(default="success", description="消息内容")
    result: Optional[DataT] = Field(default=None, description="返回数据主体")


class PageParam(BaseModel):
    """翻页接口参数"""

    page: int = Field(description="当前分页")
    limit: int = Field(description="分页大小")
    total: int = Field(description="总数据数")


class CommonMixinModel(BaseModel):
    """id、创建/更新时间Mixin Model"""

    model_config = ConfigDict(from_attributes=True)

    id: Optional[int] = Field(default=None)
    created_at: Optional[datetime] = Field(
        default=None, serialization_alias="createdAt"
    )
    update_at: Optional[datetime] = Field(default=None, serialization_alias="updateAt")


# class CommonListQueryMixinModel(BaseModel):
#     """公共列表查询schema"""

#     begin_time: Optional[str] = Field(
#         default=None,
#         description="开始时间",
#         alias="beginTime",
#     ),
#     end_time: Optional[str] = Field(
#         default=None,
#         description="结束时间",
#         alias="endTime",
#     )
#     limit: Optional[int] = Field(default=20, ge=10),
#     page: Optional[int] = Field(default=1, gt=0),
