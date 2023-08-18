import logging
from pathlib import Path
from config import config
import datetime


def set_log():
    logger = logging.getLogger(__name__)
    logger.setLevel(config.STREAM_LOG_LEVEL)
    # 判断log文件夹是否存在，不存在创建log目录
    log_directory: Path = Path(__file__).parent.parent / "log"
    if not log_directory.exists():
        os.makedirs(log_directory)
    # 文件日志处理器
    file_handler = logging.FileHandler(
        log_directory / f"{datetime.date.today()}.log",
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
