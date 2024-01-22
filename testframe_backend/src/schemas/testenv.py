from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field, ConfigDict, field_validator
from .common import PageParam, DefaultModel


class TestEnvIn(BaseModel):
    """测试环境request schema"""

    env_name: str = Field(max_length=30, description="测试环境远端地址", alias="envName")
    env_url: HttpUrl = Field(description="测试环境远端地址", alias="envUrl")
    remark: Optional[str] = Field(default=None, max_length=100, description="备注")

    @field_validator("env_url", mode="after")
    @classmethod
    def modify_env_url_after_validation(cls, value):
        """去除HttpUrl类型的多余的/"""
        return str(value).rstrip("/")


class DeleteEnvIn(BaseModel):
    """删除env schema"""

    env_ids: List[int] = Field(alias="envIds")


class TestEnvTo(DefaultModel):
    """response schema"""

    model_config = ConfigDict(from_attributes=True)

    env_name: Optional[str] = Field(default=None, serialization_alias="envName")
    env_url: Optional[str] = Field(default=None, serialization_alias="envUrl")
    remark: Optional[str] = Field(default=None)


class TestEnvsTo(PageParam):
    """环境列表response schema"""

    data: List[TestEnvTo]


class CurrentEnvIn(BaseModel):
    """设置current env"""

    env_id: int = Field(alias="envId")
