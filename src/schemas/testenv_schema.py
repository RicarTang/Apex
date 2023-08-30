from typing import Optional, List
from pydantic import BaseModel, HttpUrl, Field
from ..db.models import Testenv_Pydantic


class TestEnvIn(BaseModel):
    """测试环境request schema"""

    test_env_url: HttpUrl = Field(description="测试环境远端地址")


class TestEnvTo(Testenv_Pydantic):
    """response schema"""

    pass
