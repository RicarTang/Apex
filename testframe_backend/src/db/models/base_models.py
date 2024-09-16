from datetime import datetime
from typing import Optional
from ..enum import BoolEnum
from sqlalchemy import func, SmallInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# from sqlalchemy.ext.asyncio import AsyncAttrs


class Base(DeclarativeBase):
    """模型映射基类"""

    pass


class CommonMixin:
    """公共字段Mixin"""

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    deleted: Mapped[int] = mapped_column(
        SmallInteger,
        default=BoolEnum.FALSE.value,
        comment="逻辑删除:0=未删除,1=删除",
    )
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.now(), comment="创建时间"
    )
    update_at: Mapped[datetime] = mapped_column(
        insert_default=datetime.now(),
        onupdate=datetime.now(),
        comment="更新时间",
    )
    is_unique: Mapped[Optional[int]] = mapped_column(
        SmallInteger,
        default=1,
        comment="配合逻辑删除实现复合唯一索引;1:数据唯一,NULL:该数据删除毋须保持唯一性",
    )
