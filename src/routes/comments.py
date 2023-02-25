from fastapi import APIRouter, HTTPException
from src.models import Comments, Users
from .. import schemas
from ..utils.log_util import log
from typing import List

comment_route = APIRouter()


@comment_route.post(
    '/create',
    response_model=schemas.CommentTo
)
async def create_comment(comment: schemas.CommentIn):
    """创建comment"""
    com = await Comments.create(**comment.dict(exclude_unset=True))
    log.debug(f"com返回参数：{await com.first().values()}")
    return schemas.CommentTo(data=com)


@comment_route.get(
    '/comments/{user_id}',
    response_model=schemas.CommentsTo
)
async def get_user_comment(user_id: int):
    """获取某个user的comments"""
    try:
        user = await Users.filter(id=user_id).first().prefetch_related('comments')
        coms = await user.comments.all()
        log.debug(f"用户{user}的所有评论：{coms}")
    except AttributeError:
        raise HTTPException(status_code=202, detail="用户不存在！")
    return schemas.CommentsTo(data=coms)
