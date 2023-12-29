from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field
from ..db.models import TestenvPydantic
from .common import PageParam


class TestEnvIn(BaseModel):
    """测试环境request schema"""

    summary: str = Field(max_length=30, description="测试环境远端地址")
    test_env_url: HttpUrl = Field(description="测试环境远端地址")
    remark: Optional[str] = Field(max_length=100, description="备注")


class TestEnvTo(TestenvPydantic):
    """response schema"""

    pass


class TestEnvsTo(PageParam):
    """response schema"""

    data: List[TestenvPydantic]

class CurrentEnvIn(BaseModel):
    """设置current env"""
    env_id: int