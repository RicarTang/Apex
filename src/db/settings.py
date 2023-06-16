import config


TORTOISE_ORM = {
    "connections": {"default": config.db_url},
    "apps": {
        "models": {
            "models": ["aerich.models",config.models_path],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    # 设置时区为上海
    "timezone": "Asia/Shanghai",
}
