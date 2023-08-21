"""
项目配置文件。
"""
from pathlib import Path
from typing import Union
from pydantic import BaseSettings


class BaseConfig(BaseSettings):
    # 目录相关
    # 根目录
    ROOT_PATH: Union[str, Path] = Path(__file__).parent
    # static静态文件目录
    STATIC_PATH: Union[str, Path] = ROOT_PATH / "static"
    # casbin
    RBAC_MODEL_PATH: Union[str, Path] = (
        ROOT_PATH / "src" / "utils" / "casbin" / "rbac_model.conf"
    )
    # models
    MODELS_PATH = "src.db.models"
    # 日志配置
    STREAM_LOG_LEVEL = "DEBUG"  # log级别：'CRITICAL': CRITICAL,'FATAL': FATAL,'ERROR': ERROR,'WARN': WARNING,'WARNING': WARNING,'INFO': INFO,'DEBUG': DEBUG,'NOTSET': NOTSET
    FILE_LOG_LEVEL = "INFO"
    LOG_FORMATTER = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"
    # 数据库
    # DB_URL = "mysql://root:Mayday990812@127.0.0.1:3306/tortoise"
    DB_URL: str
    # redis  example：redis://[[name]:[pwd]]127.0.0.1:6379/0
    REDIS_URL: str
    # jwt相关
    SECRET_KEY: str
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


config = BaseConfig()
