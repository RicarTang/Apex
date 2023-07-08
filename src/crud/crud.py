"""暂时丢弃此模块。"""
from ..db.models import Users,Role,Comments
from ..utils.log_util import log


class UsersCrud:
    """用户crud."""

    @staticmethod
    async def get_user(**kwargs):
        """
        查询用户.
        :param kwargs:
            models字段,
            example：
                id = 1;
                username = "jack"
        :return: QuerySetSingle Type
        """
        return Users.get(**kwargs)

    @staticmethod
    async def create_user(**kwargs):
        """
        创建用户.
        :param kwargs: 用户输入的body
        :return: ORM Model
        """
        return await Users.create(**kwargs)

    @staticmethod
    async def query_user_role(**kwargs):
        """查询用户角色
        :param kwargs: filter条件
        :return:
        """
        user = await Users.filter(**kwargs).first().prefetch_related("roles")
        user_role = await user.roles.all()
        return user_role
