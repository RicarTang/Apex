from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from ..base_models import AbstractBaseModel
from ..enum import BoolEnum


class DataDict(AbstractBaseModel):
    """数据字典模型"""

    dict_type = fields.CharField(max_length=100, description="字典类型", index=True)
    dict_label = fields.CharField(max_length=100, description="字典label")
    dict_value = fields.CharField(max_length=100, description="label对应值")
    list_class = fields.CharField(max_length=100, description="list类", null=True)
    css_class = fields.CharField(max_length=100, description="css类", null=True)
    is_default = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="是否是默认选项,1: True,0: False",
    )
    remark = fields.CharField(max_length=100, description="备注", null=True)

    class Meta:
        table = "dict"
        ordering = ["-created_at"]
