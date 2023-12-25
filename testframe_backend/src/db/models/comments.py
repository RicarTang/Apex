from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from ..base_models import AbstractBaseModel


class Comments(AbstractBaseModel):
    """用户评论模型"""

    comment = fields.TextField(description="用户评论")
    # 外键
    user = fields.ForeignKeyField(model_name="models.Users", related_name="comments")

    class Meta:
        table = "user_comment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


# 评论schema
CommentPydantic = pydantic_model_creator(
    Comments,
    name="CommentTo",
    exclude=("is_delete",),
)
