from fastapi import Depends
from fastapi.exceptions import HTTPException
from .security import get_current_user
from .premission import PermissionAccess
from ..db.models import Users
from ..services.user import UserService



class Authority:
    """访问控制类"""

    def __init__(self, model: str, action: str):
        """
        :param model: 模块
        :param action: 权限动作
        """
        self.model = model
        self.action = action

    async def __call__(self, current_user: Users = Depends(get_current_user)):
        """
        fastapi依赖类call方法
        :param request:
        :return:
        """

        # 超级用户拥有所有权限
        is_super = await UserService.is_super_user(current_user.id)
        if is_super:
            return

        if not await PermissionAccess.has_access(
            current_user.id, self.model, self.action
        ):
            raise HTTPException(status_code=403, detail="The user has no permission!")
