from typing import List
from pydantic import BaseModel, Field
from ..db.models import CommentPydantic


class CommentIn(BaseModel):
    """
    req schema，
    用户单条评论。
    """

    # user_id: int = Field(gt=0, description="用户id")
    comment: str = Field(max_length=50, description="用户评论")


class CommentTo(CommentPydantic):
    """
    res schema，
    用户单条评论。
    """

    pass


# class CommentsTo(List[CommentPydantic]):
#     """
#     res schema，
#     某个用户的所有评论。
#     """
#     pass
