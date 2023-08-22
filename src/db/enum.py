from enum import IntEnum


class DisabledEnum(IntEnum):
    """用户disabled枚举"""

    ENABLE = 1
    DISABLE = 0


class IsSuperEnum(IntEnum):
    """true / false"""

    TRUE = 1
    FALSE = 0