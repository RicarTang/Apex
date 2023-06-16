"""
项目配置文件。
"""
# 日志配置
stream_log_level = 'DEBUG'  # log级别：'CRITICAL': CRITICAL,'FATAL': FATAL,'ERROR': ERROR,'WARN': WARNING,'WARNING': WARNING,'INFO': INFO,'DEBUG': DEBUG,'NOTSET': NOTSET
file_log_level = 'INFO'
log_formatter = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"

# 数据库
db_url = "mysql://root:123456@127.0.0.1:3306/tortoise"

# models
models_path = "src.db.models"
