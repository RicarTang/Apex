from tortoise import fields
from tortoise.contrib.pydantic import pydantic_model_creator
from .base_models import AbstractBaseModel
from .enum import (
    DisabledEnum,
    BoolEnum,
    BoolEnum,
    ApiMethodEnum,
    RequestParamTypeEnum,
)


class Users(AbstractBaseModel):
    """用户模型"""

    username = fields.CharField(max_length=20, unique=True, description="用户名")
    descriptions = fields.CharField(max_length=30, null=True, description="个人描述")
    password = fields.CharField(max_length=128, index=True, description="密码")
    is_active = fields.IntEnumField(
        enum_type=DisabledEnum,
        default=DisabledEnum.ENABLE,
        description="用户活动状态,0:disable,1:enabled",
    )
    is_super = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="用户时候是超级管理员,1: True,0: False",
    )
    # 关联关系
    comments: fields.ReverseRelation["Comments"]
    roles: fields.ManyToManyRelation["Role"]
    tokens: fields.ReverseRelation["UserToken"]

    def __str__(self):
        return str(self.username)


class Role(AbstractBaseModel):
    """角色表"""

    name = fields.CharField(max_length=20, unique=True, description="角色名称")
    description = fields.CharField(max_length=50, null=True, description="角色详情")

    # 与用户多对多关系
    users: fields.ManyToManyRelation[Users] = fields.ManyToManyField(
        model_name="models.Users", related_name="roles"
    )


class Comments(AbstractBaseModel):
    """用户评论模型"""

    comment = fields.TextField(description="用户评论")
    # 外键
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users", related_name="comments"
    )

    def __str__(self):
        return str(self.id)


class UserToken(AbstractBaseModel):
    """用户token模型"""

    token = fields.CharField(max_length=255, index=True, description="用户token令牌")
    is_active = fields.IntEnumField(
        enum_type=DisabledEnum,
        default=DisabledEnum.ENABLE,
        description="令牌状态,0:disable,1:enabled",
    )
    client_ip = fields.CharField(max_length=45, index=True, description="登录客户端IP")
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users", related_name="tokens"
    )


class TestCase(AbstractBaseModel):
    """测试用例表"""

    case_no = fields.CharField(max_length=10, unique=True, description="用例编号")
    case_title = fields.CharField(max_length=30, index=True, description="用例名称/标题")
    case_description = fields.CharField(max_length=50, null=True, description="用例说明")
    case_module = fields.CharField(max_length=20, description="用例模块")
    case_sub_module = fields.CharField(max_length=20, null=True, description="用例子模块")
    case_is_execute = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.TRUE,
        description="是否执行;1: True, 0: False",
    )
    api_path = fields.CharField(max_length=20, description="接口地址path")
    api_method = fields.CharEnumField(
        max_length=10,
        enum_type=ApiMethodEnum,
        default=ApiMethodEnum.GET,
        description="api请求方法",
    )
    request_headers = fields.CharField(max_length=500,null=True, description="请求头,必须为json")
    request_param_type = fields.CharEnumField(
        max_length=10,
        enum_type=RequestParamTypeEnum,
        default=RequestParamTypeEnum.BODY,
        description="请求参数类型;body: json类型;query: 查询参数;path: 路径参数",
    )
    request_param = fields.TextField(description="请求参数")
    expect_code = fields.IntField(description="预期状态码")
    expect_result = fields.CharField(max_length=20, null=True, description="预期结果")
    expect_data = fields.TextField(null=True, description="预期返回数据")
    request_to_redis = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="是否保存请求体到redis;1: True, 0: False",
    )
    response_to_redis = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.FALSE,
        description="是否保存响应体到redis;1: True, 0: False",
    )
    case_editor = fields.CharField(max_length=20, null=True, description="用例编写者")
    remark = fields.CharField(max_length=100, null=True, description="备注")


# 用户schema
User_Pydantic = pydantic_model_creator(
    Users, name="User", exclude=("password", "is_delete")
)
Login_pydantic = pydantic_model_creator(Users, name="Login_models")
UserIn_Pydantic = pydantic_model_creator(
    Users, name="UserIn_models", exclude_readonly=True
)
# 评论schema
Comment_Pydantic = pydantic_model_creator(Comments, name="CommentTo")
# 角色schema
Role_Pydantic = pydantic_model_creator(Role, name="RoleTo")
# 测试用例schema
Testcase_Pydantic = pydantic_model_creator(TestCase, name="TestCaseTo")
