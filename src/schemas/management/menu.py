"""菜单scheams"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from tortoise.fields.relational import ReverseRelation
from src.db.models import Routes
from src.utils.enum_util import BoolEnum

# from ..schemas.default import Routes
from ..common import PageParam, CommonMixinModel
from ...utils.log_util import log


class MenuMixinModel(BaseModel):
    """菜单Mixin"""
    name: str = Field(description="菜单名称")
    path: str = Field(description="菜单path")
    hidden: BoolEnum = Field(description="是否隐藏")
    redirect: Optional[str] = Field(default=None, description="重定向")
    component: str = Field(description="组件path")
    always_show: Optional[BoolEnum] = Field(
        default=None,
        description="是否总是显示",
        alias="alwaysShow",
    )
    status: BoolEnum = Field(description="菜单状态")


class MenuMetaMixinModel(BaseModel):
    """菜单meta Mixin"""
    title: str = Field(description="路由标题")
    icon: str = Field(description="icon图标")
    link: Optional[str] = Field(default=None, description="链接")


class MenuMetaIn(MenuMetaMixinModel):
    """菜单meta req schema"""
    no_cache: BoolEnum = Field(description="不使用keepalive", alias="noCache")


class MenuMetaOut(CommonMixinModel, MenuMetaMixinModel):
    """菜单meta res schema"""
    no_cache: BoolEnum = Field(
        description="不使用keepalive", serialization_alias="noCache"
    )


class AddMenuIn(MenuMixinModel):
    """添加路由菜单schema"""

    parent_id: Optional[int] = Field(
        default=None, description="父菜单id", alias="parentId"
    )
    meta: MenuMetaIn


class MenuTo(CommonMixinModel, MenuMixinModel):
    """menu res schmea"""

    parent_id: Optional[int] = Field(default=None, serialization_alias="parentId")
    always_show: Optional[BoolEnum] = Field(
        default=None,
        description="是否总是显示",
        serialization_alias="alwaysShow",
    )
    children: Optional[Union[List["MenuTo"], List[None]]] = Field(default=None)
    route_meta: MenuMetaOut = Field(alias="meta", validation_alias="route_meta")

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

    # @field_validator("route_meta", mode="before")
    # @classmethod
    # def modify_route_meta_befor_validator(cls, v: ReverseRelation) -> RouteMeta:
    #     """返回第一个meta(meta要求一对一)"""
    #     log.debug(v)
    #     log.debug([meta for meta in v][0])
    #     return [meta for meta in v][0]


class TreeSelectOut(BaseModel):
    """树形菜单 res schema"""

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = Field(default=None)
    label: Optional[str] = Field(
        default=None, validation_alias="route_meta", description="树形菜单label"
    )
    children: Optional[List["TreeSelectOut"]] = Field(default=None)

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


class MenuListOut(PageParam):
    """菜单列表 res schema"""
    data: List[MenuTo]


class MetaUpdateMixinModel(BaseModel):
    """更新菜单Mixin"""
    title: Optional[str] = Field(default=None, description="路由标题")
    icon: Optional[str] = Field(default=None, description="icon图标")
    link: Optional[str] = Field(default=None, description="链接")
    no_cache: Optional[BoolEnum] = Field(
        default=None, description="不使用keepalive", alias="noCache"
    )


class MenuUpdateIn(BaseModel):
    """更新菜单 req schema"""
    name: Optional[str] = Field(default=None, description="菜单名称")
    path: Optional[str] = Field(default=None, description="菜单path")
    hidden: Optional[BoolEnum] = Field(default=None, description="是否隐藏")
    redirect: Optional[str] = Field(default=None, description="重定向")
    component: Optional[str] = Field(default=None, description="组件path")
    always_show: Optional[BoolEnum] = Field(
        default=None,
        description="是否总是显示",
        alias="alwaysShow",
    )
    status: Optional[BoolEnum] = Field(default=None, description="菜单状态")
    parent_id: int = Field(default=None, alias="parentId")
    meta: Optional[MetaUpdateMixinModel] = Field(default=None)
