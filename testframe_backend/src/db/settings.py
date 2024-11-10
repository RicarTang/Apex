from ...config import config


TORTOISE_ORM = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.mysql",  # 指定数据库为mysql，必须参数
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
    "use_tz": False,
    # 设置时区为上海
    "timezone": "Asia/Shanghai",
}
