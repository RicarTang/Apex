from typing import TypeVar, Generic, Type, List, Optional, Tuple
from tortoise.models import Model
from tortoise.queryset import QuerySet

T = TypeVar("T", bound=Model)  # 泛型 T 绑定到 Tortoise 的 Model 类


class BaseRepository(Generic[T]):
    """数据访问Base Class

    Args:
        Generic (T): T为Model子类，需要指定具体的模型类

    Returns:
        _type_: _description_
    """

    model: Type[T]

    @classmethod
    async def fetch_by_pk(cls, pk: int) -> Optional[T]:
        """根据主键获取单条记录

        Args:
            pk (int): id主键

        Returns:
            Optional[T]: T | None
        """
        return await cls.model.get_or_none(pk=pk)

    @classmethod
    async def fetch_all(cls) -> List[T]:
        """获取所有记录

        Returns:
            List[T]: List[T]
        """
        return await cls.model.all()

    @classmethod
    async def fetch_all_by_filter(cls, **filters) -> List[T]:
        """根据条件查询记录

        Returns:
            List[T]: List[T]
        """
        return await cls.model.filter(**filters).all()

    @classmethod
    async def fetch_page_by_filter(
        cls, limit: int, page: int, **filters
    ) -> Tuple[List[T], int]:
        """根据分页与条件查询

        Args:
            limit (int): _description_
            page (int): _description_

        Returns:
            _type_: _description_
        """
        query = cls.model.filter(**filters)
        result = await query.offset(limit * (page - 1)).limit(limit).all()
        # total
        total = await query.count()
        return result, total

    @classmethod
    async def create(cls, **kwargs) -> T:
        """创建新记录

        Returns:
            T: Users
        """
        return await cls.model.create(**kwargs)

    @classmethod
    async def update(cls, pk: int, **kwargs) -> int:
        """根据主键更新记录

        Args:
            pk (int): id主键

        Returns:
            int: 更新数量
        """
        update_num = await cls.model.filter(pk=pk).update(**kwargs)
        return update_num

    @classmethod
    async def delete_by_pk(cls, pk: int) -> int:
        """根据主键删除记录

        Args:
            pk (int): id主键

        Returns:
            int: 删除数量
        """
        return await cls.model.filter(pk=pk).delete()

    @classmethod
    async def delete_by_filter(cls, **filters) -> int:
        """根据筛选删除记录

        Returns:
            int: 删除数量
        """
        return await cls.model.filter(**filters).delete()

    @classmethod
    async def exists(cls, **filters) -> bool:
        """根据筛选判断数据是否存在

        Returns:
            bool: _description_
        """
        is_exists = await cls.model.filter(**filters).exists()
        return is_exists
