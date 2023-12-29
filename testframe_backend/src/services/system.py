from fastapi import HTTPException, status
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from ..db.models import DataDict
from ..db.enum import DisabledEnum
from ..schemas.system import DataDictIn
from ..utils.log_util import log


class SystemService:
    """system服务"""

    @staticmethod
    async def query_dict_by_type(dict_type: str) -> DataDict:
        """根据type查询字典数据"""
        result = await DataDict.filter(dict_type=dict_type).all()
        return result

    @staticmethod
    async def add_data_dict(body: DataDictIn) -> DataDict:
        """新增字典数据"""
        result = await DataDict.create(**body.model_dump())
        return result
