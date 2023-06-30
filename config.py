"""
项目配置文件。
"""
# 日志配置
STREAM_LOG_LEVEL = 'DEBUG'  # log级别：'CRITICAL': CRITICAL,'FATAL': FATAL,'ERROR': ERROR,'WARN': WARNING,'WARNING': WARNING,'INFO': INFO,'DEBUG': DEBUG,'NOTSET': NOTSET
FILE_LOG_LEVEL = 'INFO'
LOG_FORMATTER = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"

# 数据库
DB_URL = "mysql://root:123456@127.0.0.1:3306/tortoise"

# models
MODELS_PATH = "src.db.models"
