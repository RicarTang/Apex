from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from ..base_models import AbstractBaseModel


class Routes(AbstractBaseModel):
    """前端菜单路由表"""

    name = fields.CharField(max_length=255, unique=True)
    path = fields.CharField(max_length=255)
    hidden = fields.BooleanField()
    redirect = fields.CharField(max_length=255, null=True)
    component = fields.CharField(max_length=255)
    always_show = fields.BooleanField(null=True)

    parent: fields.ReverseRelation["Routes"] = fields.ForeignKeyField(
        "models.Routes", related_name="children", null=True
    )
    meta: fields.OneToOneRelation["RouteMeta"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class RouteMeta(AbstractBaseModel):
    """菜单路由meta"""

    title = fields.CharField(max_length=255)
    icon = fields.CharField(max_length=255)
    no_cache = fields.BooleanField()
    link = fields.CharField(max_length=255, null=True)

    route: fields.OneToOneRelation["Routes"] = fields.OneToOneField(
        "models.Routes", related_name="meta"
    )

    class Meta:
        table = "route_meta"
        ordering = ["-created_at"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


RoutesPydantic = pydantic_model_creator(
    Routes,
    name="RoutesTo",
    exclude=("is_delete", "created_at", "update_at"),
)
RouteMetaPydantic = pydantic_model_creator(
    RouteMeta,
    name="RouteMetaTo",
    exclude=("is_delete", "created_at", "update_at"),
)
