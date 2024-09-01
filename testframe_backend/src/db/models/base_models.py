from datetime import datetime
from typing import Optional
from ..enum import BoolEnum
from sqlalchemy import func,Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column,declarative_base
from sqlalchemy.ext.asyncio import AsyncAttrs
# from ...db import Base

class Base(DeclarativeBase):
# class BaseModel(Base):
    """模型映射基类

    Args:
        AsyncAttrs (_type_): _description_
        DeclarativeBase (_type_): _description_
    """
    
    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    deleted: Mapped[int] = mapped_column(
        default=BoolEnum.FALSE.value,
        comment="逻辑删除:0=未删除,1=删除",
    )
    create_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        comment="创建时间",
    )
    update_at: Mapped[datetime] = mapped_column(
        insert_default=func.now(),
        onupdate=func.now(),
        comment="更新时间",
    )
    delete_at: Mapped[Optional[datetime]] = mapped_column(
        comment="删除时间",
    )

    
    
