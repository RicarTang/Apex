"""
项目配置文件。
"""
import os
ROOT_PATH = os.path.dirname(__file__)

# 日志配置
STREAM_LOG_LEVEL = 'DEBUG'  # log级别：'CRITICAL': CRITICAL,'FATAL': FATAL,'ERROR': ERROR,'WARN': WARNING,'WARNING': WARNING,'INFO': INFO,'DEBUG': DEBUG,'NOTSET': NOTSET
FILE_LOG_LEVEL = 'INFO'
LOG_FORMATTER = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"

# 数据库
DB_URL = "mysql://root:123456@127.0.0.1:3306/tortoise"

# models
MODELS_PATH = "src.db.models"

# jwt相关
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# casbin
RBAC_MODEL_PATH = os.path.join(ROOT_PATH,"src","utils","casbin","rbac_model.conf")