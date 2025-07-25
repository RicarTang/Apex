from tortoise import fields
from src.db.base_models import AbstractBaseModel
from src.utils.enum_util import (
    SuiteStatusEnum,
    BoolEnum,
    ApiMethodEnum,
    RequestParamTypeEnum,
    BoolEnum,
)


class TestCase(AbstractBaseModel):
    """测试用例表"""

    case_no = fields.CharField(max_length=10, unique=True, description="用例编号")
    case_title = fields.CharField(
        max_length=50, index=True, description="用例名称/标题"
    )
    case_description = fields.CharField(
        max_length=100, null=True, description="用例说明"
    )
    case_module = fields.CharField(max_length=20, description="用例模块")
    case_sub_module = fields.CharField(
        max_length=20, null=True, description="用例子模块"
    )
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

    class Meta:
        table = "test_case"
        ordering = ["-created_at"]


class TestSuite(AbstractBaseModel):
    """测试套件表"""

    suite_no = fields.CharField(max_length=10, unique=True, description="套件编号")
    suite_title = fields.CharField(
        max_length=50, index=True, description="套件名称/标题"
    )
    remark = fields.CharField(max_length=100, null=True, description="备注")
    status = fields.IntEnumField(
        enum_type=SuiteStatusEnum,
        default=SuiteStatusEnum.NOT_EXECUTED,
        description="测试用例执行状态;0:未执行,1:执行成功,2:执行失败",
    )
    testcases: fields.ManyToManyRelation["TestCase"] = fields.ManyToManyField(
        model_name="models.TestCase", related_name="testsuites"
    )
    task_id: fields.ReverseRelation["TestSuiteTaskId"]

    class Meta:
        table = "test_suite"
        ordering = ["-created_at"]


class TestSuiteTaskId(AbstractBaseModel):
    """测试套件与task id表"""

    task_id = fields.CharField(
        max_length=50, index=True, description="运行测试套件的task id"
    )
    testsuite: fields.OneToOneRelation["TestSuite"] = fields.OneToOneField(
        model_name="models.TestSuite", related_name="task_id"
    )

    class Meta:
        table = "test_suite_task_id"
        ordering = ["-created_at"]


class TestEnv(AbstractBaseModel):
    """测试环境表"""

    env_name = fields.CharField(max_length=30, description="测试环境名称")
    env_url = fields.CharField(max_length=50, index=True, description="测试环境地址")
    remark = fields.CharField(max_length=100, null=True, description="备注")

    class Meta:
        table = "test_environment"
        ordering = ["-created_at"]


class ScheduledTask(AbstractBaseModel):
    """定时任务表"""

    name = fields.CharField(max_length=30, description="任务唯一标识")
    task = fields.CharField(max_length=100, description="任务函数路径")
    cron_expression = fields.CharField(max_length=30, description="CRON 表达式")
    task_args = fields.CharField(max_length=200, null=True, description="任务位置参数")
    task_kwargs = fields.CharField(max_length=200, null=True, description="任务关键字参数")
    status = fields.IntEnumField(
        enum_type=BoolEnum,
        default=BoolEnum.TRUE,
        description="是否启用;1: enable, 0: disable",
    )
    last_run_at = fields.DatetimeField(description="上次执行时间")
    next_run_at = fields.DatetimeField(description="下一次执行时间")
    total_run_count = fields.IntField(default=0,description="总执行次数")
    remark = fields.CharField(max_length=100, null=True, description="备注")

    class Meta:
        table = "scheduled_task"
        ordering = ["-created_at"]
