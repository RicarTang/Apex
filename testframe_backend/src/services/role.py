from typing import Union, List, NamedTuple
from tortoise.exceptions import DoesNotExist
from tortoise.queryset import QuerySet
from ..db.models import Users, Role, Comments, UserToken, TestCase
from ..db.enum import DisabledEnum
from ..utils.log_util import log
from ..utils.exceptions.user import TokenInvalidException


class RolePermissionService:
    """角色权限crud"""

    @staticmethod
    async def query_role(**kwargs):
        """查询角色"""
        try:
            role = await Role.get(**kwargs)
        except DoesNotExist:
            return None
        return role

    @staticmethod
    async def add_role_permission(**kwargs):
        """新增角色权限(casbin_rule)"""
        # 查询role是否存在
        # 保存casbin policy
        pass