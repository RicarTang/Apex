from tortoise import fields, models
from src.utils.enum_util import BoolEnum


class AbstractBaseModel(models.Model):
    """抽象模型类"""

    id = fields.IntField(pk=True, index=True)
    is_delete = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="逻辑删除:0=未删除,1=删除",
    )
    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_at = fields.DatetimeField(auto_now=True, description="更新时间")

    class Meta:
        abstract = True
