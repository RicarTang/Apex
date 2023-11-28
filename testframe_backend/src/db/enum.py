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
