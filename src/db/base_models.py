from tortoise import fields, models







class TimeStampMixin:
    """创建/更新时间"""

    created_at = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_at = fields.DatetimeField(auto_now=True, description="更新时间")

class AbstractBaseModel(models.Model):
    id = fields.IntField(pk=True, index=True)
    is_delete = fields.IntField(
        null=False, default=0, description="逻辑删除:0=未删除,1=删除")
    
    class Meta:
        """定义为抽象模型类"""
        abstract = True