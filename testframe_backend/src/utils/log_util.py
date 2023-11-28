import sys
from pathlib import Path
from loguru import logger
from ...config import config


def log_handler():
    """日志设置"""
    # log 目录
    log_directory: Path = Path(__file__).parent.parent / "log"
    info_log_directory = log_directory / "info"
    error_log_directory = log_directory / "error"
    # 设置日志文件名格式，将日期添加到文件名中
    log_file_info = info_log_directory / "info_{time:YYYY-MM-DD}.log"
    log_file_error = error_log_directory / "error_{time:YYYY-MM-DD}.log"
    # 移除默认的输出处理器
    logger.remove()
    # 添加控制台输出处理器
    logger.add(
        sys.stdout,
        level="DEBUG",
        format=config.LOG_FORMATTER,
    )
    # 添加 info 日志处理器
    logger.add(
        log_file_info,
        rotation="00:00",
        level="INFO",
        encoding="utf-8",
        format=config.LOG_FORMATTER,
        enqueue=True,  # 进程安全
    )
    # 添加 error 日志处理器
    logger.add(
        log_file_error,
        rotation="00:00",
        level="ERROR",
        encoding="utf-8",
        format=config.LOG_FORMATTER,
        enqueue=True,
    )

    return logger


log = log_handler()

if __name__ == "__main__":
    log.debug("测试咯个哥哥in")
    log.info("测试咯个哥哥in")
