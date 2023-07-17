from typing import Optional, List
from datetime import timedelta
from fastapi import APIRouter, HTTPException, Depends, UploadFile, Request, Query
from fastapi.encoders import jsonable_encoder
from passlib.hash import md5_crypt
from tortoise.contrib.fastapi import HTTPNotFoundError
from src.db.models import User_Pydantic, Login_pydantic, Users, Role
from ..schemas import schemas
from ..utils.log_util import log
from ..core.security import create_access_token, check_jwt_auth
from ..utils import exceptions_util as exception
from ..core.authentication import Authority
from ..crud import UsersCrud


router = APIRouter()


@router.get(
    "/users",
    summary="获取所有用户",
    response_model=schemas.ResultResponse[schemas.UsersOut],
    dependencies=[Depends(check_jwt_auth)],
)
async def get_users(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取所有用户."""
    result = await User_Pydantic.from_queryset(
        Users.all().offset(limit * (page - 1)).limit(limit)
    )
    # 查询用户总数
    total = await Users.all().count()
    return schemas.ResultResponse[schemas.UsersOut](
        result=schemas.UsersOut(data=result, page=page, limit=limit, total=total)
    )


@router.get(
    "/role",
    summary="获取当前用户角色",
    response_model=schemas.ResultResponse[schemas.RolesTo],
    dependencies=[Depends(check_jwt_auth)],
)
async def query_user_role(request: Request):
    """查询当前用户角色

    Args:
        user_id (int): 用户id
    """
    log.debug(f"state用户：{request.state.user.id}")
    user_role = await UsersCrud.query_user_role(id=request.state.user.id)
    return schemas.ResultResponse[schemas.RolesTo](result=schemas.RolesTo(user_role))


@router.get(
    "/me",
    summary="获取当前用户",
    response_model=schemas.ResultResponse[schemas.UserPy],
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user,read"))],
)
async def get_current_user(
    request: Request,
    # current_user: schemas.UserPy =
):
    """获取当前用户"""
    return schemas.ResultResponse[schemas.UserPy](result=request.state.user)


@router.post(
    "/create",
    summary="创建用户",
    response_model=schemas.ResultResponse[schemas.UserOut],
)
async def create_user(user: schemas.UserIn):
    """创建用户."""
    user.password = md5_crypt.hash(user.password)
    user_obj = await Users(**user.dict(exclude_unset=True))
    # 添加用户角色
    role = await Role.filter(name=user.user_role).first()
    if not role:
        return schemas.ResultResponse[str](
            message=f"role: {user.user_role} is not exist!"
        )
    await user_obj.save()
    await user_obj.roles.add(role)
    log.info(f"成功创建用户：{user.dict(exclude_unset=True)}")
    return schemas.ResultResponse[schemas.UserOut](result=user_obj)


@router.get(
    "/{user_id}",
    response_model=schemas.ResultResponse[schemas.UserOut],
    summary="查询用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(check_jwt_auth)],
)
async def get_user(user_id: int):
    """查询单个用户."""
    log.debug(f"{await Users.get(id=user_id).values()}")
    # return await User_Pydantic.from_queryset_single(Users.get(id=user_id))
    user = await Users.get(id=user_id)
    return schemas.ResultResponse[schemas.UserOut](result=user)


@router.put(
    "/{user_id}",
    response_model=schemas.ResultResponse[schemas.UserOut],
    summary="更新用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user,update"))],
)
async def update_user(user_id: int, user: schemas.UserIn):
    """更新用户信息."""
    user.password = md5_crypt.hash(user.password)
    result = await Users.filter(id=user_id).update(**user.dict(exclude_unset=True))
    log.debug(f"update更新{result}条数据")
    return schemas.ResultResponse[schemas.UserOut](result=await Users.get(id=user_id))


@router.delete(
    "/{user_id}",
    response_model=schemas.ResultResponse[str],
    summary="删除用户",
    responses={404: {"model": HTTPNotFoundError}},
    dependencies=[Depends(check_jwt_auth), Depends(Authority("user,delete"))],
)
async def delete_user(user_id: int):
    """删除用户."""
    deleted_count = await Users.filter(id=user_id).delete()
    log.debug("")
    if not deleted_count:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return schemas.ResultResponse[str](message=f"Deleted user {user_id}")


@router.post(
    "/login", summary="登录", response_model=schemas.ResultResponse[schemas.Login]
)
async def login(user: schemas.LoginIn, request: Request):
    """用户登陆."""

    # 查询数据库有无此用户
    query_user = await Login_pydantic.from_tortoise_orm(
        await Users.get(username=user.username)
    )
    # 序列化Pydantic对象
    db_user = jsonable_encoder(query_user)
    # 验证密码
    if not md5_crypt.verify(secret=user.password, hash=query_user.password):
        return schemas.ResultResponse[str](message="Password Error!")
    if not query_user.is_active:
        # return schemas.ResultResponse[str](message="The user status is unavailable!")
        raise HTTPException(status_code=403, detail="The user status is unavailable!")
    # 创建jwt
    access_token = create_access_token(data={"sub": query_user.username})
    # db_user["access_token"] = access_token
    return schemas.ResultResponse[schemas.Login](
        result=schemas.Login(
            data=db_user, access_token=access_token, token_type="bearer"
        )
    )


@router.post("/uploadfile", deprecated=True)
async def uploadfile(file: UploadFile):
    with open(f"./src/static/{file.filename}", "wb") as f:
        f.write(await file.read())

    return {"filename": file.filename}
