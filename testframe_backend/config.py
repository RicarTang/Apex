"""
项目配置文件。
"""
from pathlib import Path
from typing import Union
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env", env_file_encoding="utf-8"
    )
    # 目录相关
    # 根目录
    ROOT_PATH: Union[str, Path] = Path(__file__).parent
    # static静态文件目录
    STATIC_PATH: Union[str, Path] = ROOT_PATH / "static"
    # 测试目录
    TEST_PATH: Union[str, Path] = ROOT_PATH / "src" / "autotest"

    # casbin
    RBAC_MODEL_PATH: Union[str, Path] = (
        ROOT_PATH / "src" / "utils" / "casbin" / "rbac_model.conf"
    )
    # autotest 配置路径
    TEST_CONFIG_PATH: Union[str, Path] = TEST_PATH / "config" / "config.yaml"
    # models
    MODELS_PATH: str = "testframe_backend.src.db.models"
    # 日志配置
    STREAM_LOG_LEVEL: str = "DEBUG"  # log级别：'CRITICAL': CRITICAL,'FATAL': FATAL,'ERROR': ERROR,'WARN': WARNING,'WARNING': WARNING,'INFO': INFO,'DEBUG': DEBUG,'NOTSET': NOTSET
    FILE_LOG_LEVEL: str = "INFO"
    # LOG_FORMATTER = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"
    LOG_FORMATTER: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    # 数据库
    # DB_URL = "mysql://root:Mayday990812@127.0.0.1:3306/tortoise"
    DB_URL: str
    # redis  example：redis://:123456@127.0.0.1:6379/0
    REDIS_URL: str

    # jwt相关
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7


config = BaseConfig()

if __name__ == "__main__":
    print(config.model_dump())
