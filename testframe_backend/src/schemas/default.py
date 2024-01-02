from typing import List
from pydantic import Field, field_validator
from tortoise.fields.relational import ReverseRelation
from ..db.models import RouteMetaPydantic, RoutesPydantic, RouteMeta
from ..utils.log_util import log


class Routes(RoutesPydantic):
    route_meta: RouteMetaPydantic = Field(alias="meta",validation_alias="route_meta")

    @field_validator("route_meta", mode="before")
    @classmethod
    def modify_route_meta_befor_validator(cls, v: ReverseRelation) -> RouteMeta:
        """返回第一个meta(meta要求一对一)"""
        return [meta for meta in v][0]


class RoutesTo(Routes):
    """routes res"""

    children: List[Routes]
