from typing import Optional, List
from pydantic import BaseModel, Field
from ..db.models import DataDictPydantic
from ..db.enum import BoolEnum


class TreeSelectTo(BaseModel):
    """树形菜单"""

    id: int
    title: str = Field(description="meta title", alias="label")
    children: Optional[List["TreeSelectTo"]]
