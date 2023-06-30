import config


TORTOISE_ORM = {
    "connections": {"default": config.DB_URL},
    "apps": {
        "models": {
            "models": ["aerich.models",config.MODELS_PATH],
            "default_connection": "default",
        }
    },
    "use_tz": False,
    # 设置时区为上海
    "timezone": "Asia/Shanghai",
}
