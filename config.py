"""
项目配置文件。
"""
import os
from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    ROOT_PATH: str = os.path.dirname(__file__)
    # 日志配置
    STREAM_LOG_LEVEL = "DEBUG"  # log级别：'CRITICAL': CRITICAL,'FATAL': FATAL,'ERROR': ERROR,'WARN': WARNING,'WARNING': WARNING,'INFO': INFO,'DEBUG': DEBUG,'NOTSET': NOTSET
    FILE_LOG_LEVEL = "INFO"
    LOG_FORMATTER = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"
    # 数据库
    # DB_URL = "mysql://root:Mayday990812@127.0.0.1:3306/tortoise"
    DB_URL: str
    # models
    MODELS_PATH = "src.db.models"
    # jwt相关
    SECRET_KEY: str
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    # casbin
    RBAC_MODEL_PATH = os.path.join(
        ROOT_PATH, "src", "utils", "casbin", "rbac_model.conf"
    )


config = BaseConfig()
