from typing import Optional, List, Union, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from tortoise.fields.relational import ReverseRelation
from ..db.models import Routes, RouteMeta
from ..db.enum import BoolEnum, DisabledEnum

# from ..schemas.default import Routes
from .common import PageParam, DefaultModel
from ..utils.log_util import log


class Menu(BaseModel):
    name: str = Field(description="菜单名称")
    path: str = Field(description="菜单path")
    hidden: BoolEnum = Field(description="是否隐藏")
    redirect: Optional[str] = Field(default=None, description="重定向")
    component: str = Field(description="组件path")
    always_show: Optional[BoolEnum] = Field(
        default=None, description="是否总是显示", alias="alwaysShow"
    )
    status: DisabledEnum = Field(description="菜单状态")


class MenuMeta(BaseModel):
    title: str = Field(description="路由标题")
    icon: str = Field(description="icon图标")
    no_cache: BoolEnum = Field(
        description="不使用keepalive", alias="noCache"
    )
    link: Optional[str] = Field(default=None, description="链接")


class MenuMetaTo(DefaultModel, MenuMeta):
    pass


class AddMenuIn(Menu):
    """添加路由菜单schema"""

    parent_id: Optional[int] = Field(
        default=None, description="父菜单id", serialization_alias="parentId"
    )
    meta: MenuMeta


class MenuTo(DefaultModel, Menu):
    """res schmea"""

    children: Optional[Union[List["MenuTo"], List[None]]] = Field(default=None)
    route_meta: MenuMetaTo = Field(alias="meta", validation_alias="route_meta")

    @field_validator("children", mode="before")
    @classmethod
    def modify_children_befor_validator(
        cls, v: ReverseRelation
    ) -> Union[Routes, List[None]]:
        """
        有children返回,没有返回None
        TODO 多层嵌套children时的处理
        """
        try:
            result = [children for children in v]
        except Exception:
            result = []
        return result

    @field_validator("route_meta", mode="before")
    @classmethod
    def modify_route_meta_befor_validator(cls, v: ReverseRelation) -> RouteMeta:
        """返回第一个meta(meta要求一对一)"""
        return [meta for meta in v][0]


class TreeSelectTo(BaseModel):
    """树形菜单"""

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = Field(default=None)
    label: Optional[str] = Field(
        default=None, validation_alias="route_meta", description="树形菜单label"
    )
    children: Optional[List["TreeSelectTo"]] = Field(default=None)

    @field_validator("label", mode="before")
    @classmethod
    def modify_label_before_validation(cls, value):
        """模型验证前修改入参"""
        try:
            label = value[0].title
        except TypeError:
            label = value.title
        except AttributeError as e:
            # orm对象返回空，不做处理
            log.error(e)
        return label

    @field_validator("children", mode="before")
    @classmethod
    def modify_children_before_validation(cls, value):
        """模型验证前修改入参"""

        try:
            res = [MenuTo.model_validate(children) for children in value]
            return res
        except AttributeError as e:
            # orm对象返回空，不做处理
            log.error(e)


class MenuListTo(PageParam):
    data: List[MenuTo]
