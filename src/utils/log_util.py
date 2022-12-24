import logging
import os


def set_log():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    # 文件日志处理器
    file_handler = logging.FileHandler(os.path.join(os.path.dirname(__file__),'../log/log.log'), encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    log_format = logging.Formatter(
        "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s")
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)
    # 控制台日志处理器
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)
    return logger


log = set_log()

if __name__ == '__main__':
    log.debug("测试咯个哥哥in")
    log.info("测试咯个哥哥in")
