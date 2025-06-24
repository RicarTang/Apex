"""
项目配置文件。
"""

from pathlib import Path
from typing import Union, Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent / ".env",
        env_file_encoding="utf-8",
        extra="allow",
    )
    # 目录相关
    ## 根目录
    ROOT_PATH: Union[str, Path] = Path(__file__).parent
    ## static静态文件目录
    STATIC_PATH: Union[str, Path] = ROOT_PATH / "static"
    ## 测试目录
    TEST_PATH: Union[str, Path] = ROOT_PATH / "autotest"
    ## pytest测试结果输出目录
    PYTEST_DATA: Union[str, Path] = TEST_PATH / "report" / "pytest_data"
    ## allure report 目录
    ALLURE_REPORT: Union[str, Path] = TEST_PATH / "report" / "allure_report"
    ## 是否使用StaticFiles, 默认使用StaticFiles,还可配置nginx提高性能(使用nginx时这个配置配置为False)
    ON_STATICFILES: bool = True
    ## autotest 配置路径
    TEST_CONFIG_PATH: Union[str, Path] = TEST_PATH / "config" / "config.yaml"
    ## orm models路径
    MODELS_PATH: str = "src.db.models"

    # 日志配置
    ## 控制台日志级别
    STREAM_LOG_LEVEL: Literal[
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    ] = "DEBUG"

    ## 保存至.log的日志级别
    FILE_LOG_LEVEL: Literal[
        "TRACE", "DEBUG", "INFO", "SUCCESS", "WARNING", "ERROR", "CRITICAL"
    ] = "INFO"
    ## 日志格式
    ## LOG_FORMATTER = "%(levelname)s:     %(asctime)s - %(filename)s - %(funcName)s - line: %(lineno)d - message: %(message)s"
    LOG_FORMATTER: str = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )

    # 数据库
    DB_ENGINE: Literal["mysql", "asyncpg", "sqlite", "mssql"] = "mysql"  # 数据库引擎
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_DATEBASE: str
    USE_TZ: bool = False  # 是否启用UTC时区
    TZ: str = "Asia/Shanghai"  # 数据库时区

    # redis
    ## example：redis://:123456@127.0.0.1:6379/0
    REDIS_URL: str

    # celery
    ## celery backend url, example: "db+mysql+pymysql://root:123456@127.0.0.1:3306/tortoise"(数据库作为backend)
    CELERY_BACKEND: str
    ## celery broker url, example：redis://:123456@127.0.0.1:6379/1
    CELERY_BROKER: str
    ## celery从数据库导入定时任务的间隔时间（s）
    CELERY_BEAT_CHECK_INTERVAL: int = 300

    # jwt相关
    ## jwt私钥, 使用openssl rand -hex 32快捷生成可靠私钥
    SECRET_KEY: str
    ## jwt算法
    ALGORITHM: str = "HS256"
    ## jwt过期时间,单位s
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    # swagger
    SWAGGER_TITLE: str = "api swagger"
    SWAGGER_VERSION: str = "1.0"
    SWAGGER_DES: str = "fastapi+tortoise-orm async web framework"
    SWAGGER_JS_URL: str = "/static/swagger-ui/swagger-ui-bundle.js"  # 使用本地文件
    SWAGGER_CSS_URL: str = "/static/swagger-ui/swagger-ui.css"
    SWAGGER_FAVICON_URL: str = "https://fastapi.tiangolo.com/img/favicon.png"


config = BaseConfig()

if __name__ == "__main__":
    print(config.model_dump())
