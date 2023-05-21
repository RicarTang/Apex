from fastapi import APIRouter, Depends
from src.models import Comments, Users
from .. import schemas
from ..utils.log_util import log
from ..utils import security_util, exceptions_util as exception

comment_api = APIRouter()


@comment_api.post("/create", summary="发表评论", response_model=schemas.CommentTo)
async def create_comment(comment: schemas.CommentIn):
    """创建comment"""
    com = await Comments.create(**comment.dict(exclude_unset=True))
    log.debug(f"com返回参数：{await com.first().values()}")
    return schemas.CommentTo(data=com)


@comment_api.get(
    "/comments/{user_id}", summary="获取用户评论", response_model=schemas.CommentsTo
)
async def get_user_comment(user_id: int):
    """获取某个user的comments"""
    try:
        user = await Users.filter(id=user_id).first().prefetch_related("comments")
        coms = await user.comments.all()
        log.debug(f"用户{user}的所有评论：{coms}")
    except AttributeError:
        raise exception.ResponseException(content="用户不存在！")
    return schemas.CommentsTo(data=coms)


@comment_api.get("/me", summary="获取我的评论", response_model=schemas.CommentsTo)
async def get_comments_me(
    current_user: schemas.UserPy = Depends(security_util.get_current_user),
):
    """当前用户的所有评论"""
    user = (
        await Users.filter(username=current_user.username)
        .first()
        .prefetch_related("comments")
    )
    comments = await user.comments.all()
    log.debug(f"comments:{comments}")
    return schemas.CommentsTo(data=comments)
