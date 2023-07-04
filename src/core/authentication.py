from fastapi import Request,Depends
from fastapi.exceptions import HTTPException
from casbin import Enforcer
from casbin_tortoise_adapter import TortoiseAdapter, CasbinRule
from .security import check_jwt_auth
from .. import schemas
import config
from ..utils.log_util import log


# tortoise-orm casbin适配器
adapter = TortoiseAdapter()
enforcer = Enforcer(config.RBAC_MODEL_PATH, adapter)


async def get_current_user_authorization(request:Request,current_user: schemas.UserPy = Depends(check_jwt_auth)):
    """校验用户访问权限"""
    log.debug(await CasbinRule.all())
    # 因为casbin的load_policy方法不是异步加载，所以得手动加载策略
    await adapter.load_policy(enforcer.get_model())
    sub = current_user.username
    obj = request.url.path
    act = request.method
    if not(enforcer.enforce(sub, obj, act)):
        raise HTTPException(
            status_code=403,
            detail="Method not authorized for this user")
    return current_user

