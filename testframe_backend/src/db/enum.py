from enum import IntEnum, Enum


class DisabledEnum(IntEnum):
    """用户disabled枚举"""

    ENABLE = 1
    DISABLE = 0


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
