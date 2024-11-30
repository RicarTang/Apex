from enum import IntEnum, Enum

class BoolEnum(IntEnum):
    """true / false"""

    TRUE = 1
    FALSE = 0


class ApiMethodEnum(str, Enum):  # 继承str以便pydantic验证
    """api方法"""

    GET = "get"
    POST = "post"
    UPDATE = "update"
    PUT = "put"
    DELETE = "delete"
    OPTIONS = "options"


class RequestParamTypeEnum(str, Enum):
    """请求参数类型"""

    BODY = "body"
    QUERY = "query"
    PATH = "path"


class AccessActionEnum(str, Enum):
    """访问控制action"""

    ADD = "add"
    DEL = "delete"
    PUT = "update"
    GET = "query"


class AccessModelEnum(str, Enum):
    """访问控制model"""

    USER = "user"
    ADMIN = "admin"
    APITEST = "apitest"


class SuiteStatusEnum(IntEnum):
    """套件状态"""

    NOT_EXECUTED = 0
    EXECUTED_OK = 1
    EXECUTED_FAILED = 2


class ScheduleTaskStatusEnum(IntEnum):
    """定时任务状态"""

    PENDING = 0
    RUNNING = 1
    COMPLETED = 2
    FAILED = 3
    PAUSED = 4