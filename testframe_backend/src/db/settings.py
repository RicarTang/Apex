from ...config import config


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
