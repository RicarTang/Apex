import json
from datetime import datetime


def publish_format(message: str, status: int):
    """格式化发布消息的message"""
    try:
        return json.dumps(
            dict(status=status, message=f"{datetime.now()} | {message}"),
            ensure_ascii=False,
        )
    except json.JSONDecodeError as e:
        raise e
