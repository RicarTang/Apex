import logging
import os
from config import config
import datetime


def set_log():
    logger = logging.getLogger(__name__)
    logger.setLevel(config.STREAM_LOG_LEVEL)
    # 判断log文件夹是否存在，不存在创建log目录
    is_exists = os.path.exists(os.path.join(os.path.dirname(__file__), "../log"))
    if not is_exists:
        os.makedirs(os.path.join(os.path.dirname(__file__), "../log"))
    # 文件日志处理器
    file_handler = logging.FileHandler(
        os.path.join(os.path.dirname(__file__), f"../log/{datetime.date.today()}.log"),
        encoding="utf-8",
    )
    file_handler.setLevel(config.FILE_LOG_LEVEL)
    log_format = logging.Formatter(config.LOG_FORMATTER)
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    # 控制台日志处理器
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)
    return logger


log = set_log()

if __name__ == "__main__":
    log.debug("测试咯个哥哥in")
    log.info("测试咯个哥哥in")
