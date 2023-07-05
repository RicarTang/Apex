from typing import Any
from fastapi import Request, Depends
from fastapi.exceptions import HTTPException
from casbin import Enforcer
from casbin_tortoise_adapter import TortoiseAdapter, CasbinRule
from .security import check_jwt_auth
from .. import schemas
import config
from ..utils.log_util import log
from .util import Singleton


class TortoiseCasbin(metaclass=Singleton):
    def __init__(self, model: str) -> None:
        adapter = TortoiseAdapter()
        self.enforcer = Enforcer(str(model), adapter)

    async def has_permission(self, user: str, model: str, act: str) -> bool:
        """
        判断是否拥有权限
        """
        return self.enforce.enforce(user, model, act)

    async def add_permission_for_role(self, role: str, model: str, act: str):
        """
        添加角色权限
        """
        return await self.enforce.add_policy(role, model, act)

    async def remove_permission_for_role(self, role: str, model: str, act: str):
        return await self.enforce.remove_policy(role, model, act)

    def __getattr__(self, attr: str) -> Any:
        return getattr(self.enforce, attr)


class Authority:
    """认证类"""

    def __init__(self, policy: str) -> None:
        self.policy = policy

    async def __call__(self, request: Request, *args: Any, **kwds: Any) -> Any:
        """
        超级管理员不需要进行权限认证
        :param request:
        :return:
        """
        model, act = self.policy.split(",")
        e = await get_casbin()

        # 超级用户拥有所有权限
        if request.state.user.is_super:
            return

        if not await e.has_permission(request.state.user.username, model, act):
            raise HTTPException(
                status_code=403, detail="Method not authorized for this user"
            )


# async def get_current_user_authorization(request:Request,current_user: schemas.UserPy = Depends(check_jwt_auth)):
#     """校验用户访问权限"""
#     log.debug(await CasbinRule.all())
#     # 因为casbin的load_policy方法不是异步加载，所以得手动加载策略
#     await adapter.load_policy(e.get_model())
#     await adapter.add_policy("","p",["admin","*","*"])
#     sub = current_user.username
#     obj = request.url.path
#     act = request.method
#     if not(e.enforce(sub, obj, act)):
#         raise HTTPException(
#             status_code=403,
#             detail="Method not authorized for this user")
#     return current_user


async def get_casbin() -> TortoiseCasbin:
    """
    获取 casbin 权限认证对象，初始化时要加载一次权限模型信息
    :return:
    """
    tor_casbin = TortoiseCasbin(config.RBAC_MODEL_PATH)
    if not hasattr(tor_casbin, "load"):
        setattr(tor_casbin, "load", True)
        await tor_casbin.load_policy()
    return tor_casbin
