from pydantic import Field, BaseModel, ConfigDict
from ..schemas.user import UserTo


class Login(BaseModel):
    """登录res schema"""

    data: UserTo = Field(description="用户信息主体")
    access_token: str = Field(description="jwt")
    token_type: str = Field(description="token类型")


class LoginIn(BaseModel):
    """登录req schema"""

    model_config = ConfigDict(
        json_schema_extra={"example": {"username": "admin", "password": "123456"}}
    )

    username: str = Field(min_length=2, max_length=20)
    password: str = Field(min_length=6, max_length=20)
