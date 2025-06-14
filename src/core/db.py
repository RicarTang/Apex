from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.config import config

# orm config
TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": f"tortoise.backends.{config.DB_ENGINE}",  # 指定数据库，必须参数
            "credentials": {
                "host": config.DB_HOST,  # 数据库地址
                "port": config.DB_PORT,  # 数据库端口
                "user": config.DB_USER,  # 用户名
                "password": config.DB_PASSWORD,  # 密码
                "database": config.DB_DATEBASE,  # 数据库名
            },
        }
    },
    "apps": {
        "models": {
            "models": ["aerich.models", config.MODELS_PATH],
            "default_connection": "default",
        }
    },
    "use_tz": config.USE_TZ,
    # 设置数据库datetime时区
    "timezone": config.TZ,
}


def register_db(app: FastAPI):
    """注册tortoise

    Args:
        app (FastAPI): _description_
    """
    register_tortoise(
        app,
        config=TORTOISE_ORM,
        generate_schemas=False,  # 重启服务时自动生成数据库表；关闭，改为使用aerich
        add_exception_handlers=True,
    )
