from tortoise import fields
from src.db.base_models import AbstractBaseModel
from src.utils.enum_util import BoolEnum


class Routes(AbstractBaseModel):
    """前端菜单路由表"""

    name = fields.CharField(max_length=255, unique=True)
    path = fields.CharField(max_length=255)
    hidden = fields.BooleanField()
    redirect = fields.CharField(max_length=255, null=True)
    component = fields.CharField(max_length=255)
    always_show = fields.BooleanField(null=True)
    status = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.TRUE,
        description="菜单可用状态,0:disable,1:enabled",
    )
    parent: fields.ReverseRelation["Routes"] = fields.ForeignKeyField(
        "models.Routes", related_name="children", null=True
    )
    # route_meta: fields.ReverseRelation["RouteMeta"]
    route_meta: fields.ForeignKeyRelation["RouteMeta"] = fields.ForeignKeyField(
        "models.RouteMeta", related_name="route_meta"
    )

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class RouteMeta(AbstractBaseModel):
    """菜单路由meta"""

    title = fields.CharField(max_length=255)
    icon = fields.CharField(max_length=255)
    no_cache = fields.BooleanField()
    link = fields.CharField(max_length=255, null=True)
    # route: fields.ForeignKeyRelation["Routes"] = fields.ForeignKeyField(
    #     "models.Routes", related_name="route_meta"
    # )
    route: fields.ReverseRelation["Routes"]

    class Meta:
        table = "route_meta"
        ordering = ["-created_at"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"
