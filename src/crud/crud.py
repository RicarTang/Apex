"""暂时丢弃此模块。"""
from ..models import Users
from ..utils.log_util import log


class UsersCrud:
    """用户crud."""

    @staticmethod
    async def get(**kwargs):
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
    async def create(**kwargs):
        """
        创建用户.
        :param kwargs: 用户输入的body
        :return: ORM Model
        """
        return await Users.create(**kwargs)
