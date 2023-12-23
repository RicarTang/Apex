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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class Role(AbstractBaseModel):
    """角色表"""

    name = fields.CharField(max_length=20, unique=True, description="角色名称")
    description = fields.CharField(max_length=50, null=True, description="角色详情")

    # 与用户多对多关系
    users: fields.ManyToManyRelation[Users] = fields.ManyToManyField(
        model_name="models.Users", related_name="roles"
    )

    class Meta:
        ordering = ["-created_at"]


class Comments(AbstractBaseModel):
    """用户评论模型"""

    comment = fields.TextField(description="用户评论")
    # 外键
    user: fields.ForeignKeyRelation[Users] = fields.ForeignKeyField(
        model_name="models.Users", related_name="comments"
    )

    class Meta:
        table = "user_comment"
        ordering = ["-created_at"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


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

    class Meta:
        table = "user_token"


class Routes(AbstractBaseModel):
    """前端路由表"""

    name = fields.CharField(max_length=255)
    path = fields.CharField(max_length=255)
    hidden = fields.BooleanField()
    redirect = fields.CharField(max_length=255, null=True)
    component = fields.CharField(max_length=255)
    always_show = fields.BooleanField(null=True)
    is_admin_visible = fields.BooleanField(null=True)

    parent: fields.ReverseRelation["Routes"] = fields.ForeignKeyField(
        "models.Routes", related_name="children", null=True
    )

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class RouteMeta(AbstractBaseModel):
    """路由meta"""

    title = fields.CharField(max_length=255)
    icon = fields.CharField(max_length=255)
    no_cache = fields.BooleanField()
    link = fields.CharField(max_length=255, null=True)

    route: fields.OneToOneRelation["Routes"] = fields.OneToOneField(
        "models.Routes", related_name="meta"
    )

    class Meta:
        table = "route_meta"
        ordering = ["-created_at"]

    def __str__(self):
        return f"<{self.__class__.__name__},id:{self.id}>"


class TestCase(AbstractBaseModel):
    """测试用例表"""

    case_no = fields.CharField(max_length=10, unique=True, description="用例编号")
    case_title = fields.CharField(max_length=50, index=True, description="用例名称/标题")
    case_description = fields.CharField(max_length=100, null=True, description="用例说明")
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
    request_headers = fields.CharField(
        max_length=500, null=True, description="请求头,必须为json"
    )
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
    testsuites: fields.ManyToManyRelation["TestSuite"] = fields.ManyToManyField(
        model_name="models.TestSuite"
    )

    class Meta:
        table = "test_case"
        ordering = ["-created_at"]


class TestSuite(AbstractBaseModel):
    """测试套件表"""

    suite_no = fields.CharField(max_length=10, unique=True, description="套件编号")
    suite_title = fields.CharField(max_length=50, index=True, description="套件名称/标题")
    remark = fields.CharField(max_length=100, null=True, description="备注")
    testcases: fields.ManyToManyRelation["TestCase"] = fields.ManyToManyField(
        model_name="models.TestCase"
    )
    task_id: fields.ReverseRelation["TestSuiteTaskId"]

    class Meta:
        table = "test_suite"
        ordering = ["-created_at"]


class TestSuiteTaskId(AbstractBaseModel):
    """测试套件与task id表"""

    task_id = fields.CharField(max_length=50, index=True, description="运行测试套件的task id")
    testsuite: fields.OneToOneRelation[TestSuite] = fields.OneToOneField(
        model_name="models.TestSuite", related_name="task_id"
    )

    class Meta:
        table = "test_suite_task_id"
        ordering = ["-created_at"]


class TestEnv(AbstractBaseModel):
    """测试环境表"""

    summary = fields.CharField(max_length=30, description="测试环境名称")
    test_env_url = fields.CharField(max_length=50, index=True, description="测试环境地址")
    remark = fields.CharField(max_length=100, null=True, description="备注")

    class Meta:
        table = "test_environment"
        ordering = ["-created_at"]


# response schema
# 用户schema
UserPydantic = pydantic_model_creator(
    Users,
    name="UserTo",
    exclude=("password", "is_delete"),
)
# 评论schema
CommentPydantic = pydantic_model_creator(
    Comments,
    name="CommentTo",
    exclude=("is_delete",),
)
# 角色schema
RolePydantic = pydantic_model_creator(
    Role,
    name="RoleTo",
    exclude=("is_delete",),
)
# 测试用例schema
TestcasePydantic = pydantic_model_creator(
    TestCase,
    name="TestCaseTo",
    exclude=("is_delete",),
)
# 测试套件schema
TestsuitePydantic = pydantic_model_creator(
    TestSuite,
    name="TestSuiteTo",
    exclude=("is_delete",),
)
# 测试环境schema
TestenvPydantic = pydantic_model_creator(
    TestEnv,
    name="TestEnvTo",
    exclude=("is_delete",),
)
RoutesPydantic = pydantic_model_creator(
    Routes,
    name="RoutesTo",
    exclude=("is_delete", "id", "created_at", "update_at"),
)
RouteMetaPydantic = pydantic_model_creator(
    RouteMeta,
    name="RouteMetaTo",
    exclude=("is_delete", "id", "created_at", "update_at"),
)
