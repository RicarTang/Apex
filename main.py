from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise
from src.routes import user_route, comment_route, test_route
import config
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.utils.exceptions_util import ResponseException, response_exception
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="api swagger",
              version="1.0",
              description="fastapi+tortoise-orm async web framework")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
# router
app.include_router(user_route, tags=['User'], prefix='/user')
app.include_router(comment_route, tags=['Comment'], prefix='/comment')
# app.include_router(test_route, tags=['Test'], prefix='/test')
# exception
app.add_exception_handler(ResponseException, response_exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request,
                                       exc: RequestValidationError):
    """修改默认的请求验证错误模型"""
    return JSONResponse(status_code=422,
                        content={
                            "success": False,
                            "detail": exc.errors()
                        })
