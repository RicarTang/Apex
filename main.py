from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from src.routes import user_route
import config

app = FastAPI(
    title="api swagger",
    version="1.0",
    description="fastapi+tortoise-orm async web framework"
)
register_tortoise(
    app,
    config={
        'connections': {
            'default': config.db_url
        },
        'apps': {
            'models': {
                "models": [config.models_path],
                'default_connection': 'default',
            }
        },
        "use_tz": False,
        # 设置时区为上海
        "timezone": "Asia/Shanghai",
    },
    generate_schemas=True,  # 重启服务时自动生成数据库表
    add_exception_handlers=True,
)
app.include_router(user_route, tags=['User'], prefix='/user')
