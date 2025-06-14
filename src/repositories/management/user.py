"""用户数据访问模块"""

from typing import Tuple, List
from ...repositories import BaseRepository
from ...db.models import Users


class UserRepository(BaseRepository[Users]):
    """用户数据访问仓库

    Args:
        BaseRepository (_type_): _description_
    """

    model = Users

    @classmethod
    async def fetch_by_pk_with_roles(cls, pk: int) -> Users:
        """查询主键id预取关联role

        Args:
            id (int): id主键

        Returns:
            Users: Users模型对象
        """
        user = await cls.model.get_or_none(pk=pk).prefetch_related("roles")
        return user

    @classmethod
    async def fetch_by_filter_with_roles(cls, pk: int, **filter) -> Users:
        """根据筛选条件查询用户并预取关联role

        Returns:
            Users: _description_
        """
        user = (
            await cls.model.filter(pk=pk, roles__is_super=True)
            .first()
            .prefetch_related("roles")
        )
        return user

    @classmethod
    async def fetch_user_list_by_filter_with_roles(
        cls, limit: int, page: int, **filters
    ) -> Tuple[List[Users], int]:
        """查询用户列表预取关联role

        Returns:
            Tuple[List[Users], int]: _description_
        """
        query = Users.filter(**filters)
        result = (
            await query.prefetch_related("roles")
            .offset(limit * (page - 1))
            .limit(limit)
            .all()
        )
        # total
        total = await query.count()
        return result, total
