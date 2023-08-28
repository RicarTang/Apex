from typing import List
from pydantic import BaseModel, Field
from ..db.models import Comment_Pydantic


class CommentIn(BaseModel):
    """
    req schema，
    用户单条评论。
    """

    # user_id: int = Field(gt=0, description="用户id")
    comment: str = Field(max_length=50, description="用户评论")


class CommentTo(Comment_Pydantic):
    """
    res schema，
    用户单条评论。
    """

    pass


class CommentsTo(List[Comment_Pydantic]):
    """
    res schema，
    某个用户的所有评论。
    """

    pass
