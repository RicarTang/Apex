from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from ..db.models import Routes, RouteMetaPydantic, RoutesPydantic
from ..db.enum import BoolEnum
from ..schemas.default import Routes
from ..utils.log_util import log


class TreeSelectTo(BaseModel):
    """树形菜单"""

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = Field(default=None)
    label: Optional[str] = Field(
        default=None, validation_alias="meta", description="树形菜单label"
    )
    # children: Optional[List[Routes]] = Field(default=None)
    children: Optional[List["TreeSelectTo"]] = Field(default=None)

    @field_validator("label", mode="before")
    @classmethod
    def modify_label_before_validation(cls, value):
        """模型验证前修改入参"""
        try:
            return value.title
        except AttributeError as e:
            # orm对象返回空，不做处理
            log.error(e)

    @field_validator("children", mode="before")
    @classmethod
    def modify_children_before_validation(cls, value):
        """模型验证前修改入参"""

        try:
            res = [Routes.from_orm(children) for children in value]
            return res
        except AttributeError as e:
            # orm对象返回空，不做处理
            log.error(e)


class MenuMeta(BaseModel):
    title: str = Field(description="路由标题")
    icon: str = Field(description="icon图标")
    no_cache: BoolEnum = Field(description="不使用keepalive")
    link: Optional[str] = Field(default=None, description="链接")


class AddMenuIn(BaseModel):
    """添加路由菜单schema"""

    name: str = Field(description="菜单名称")
    path: str = Field(description="菜单path")
    hidden: BoolEnum = Field(description="是否隐藏")
    redirect: Optional[str] = Field(default=None, description="重定向")
    component: str = Field(description="组件path")
    always_show: Optional[BoolEnum] = Field(default=None, description="是否总是显示")
    parent_id: Optional[int] = Field(default=None, description="父菜单id")
    meta: MenuMeta


class AddMenuTo(RoutesPydantic):
    meta: RouteMetaPydantic
    children: Optional[RoutesPydantic] = Field(default=None)
