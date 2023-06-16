from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise
from src.api import user_api, comment_api, test_api

# import config
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from src.utils.exceptions_util import ResponseException, response_exception
from src.utils.background_task_util import scheduler
from src.utils.log_util import log
from fastapi.middleware.cors import CORSMiddleware
from src.db.settings import TORTOISE_ORM

app = FastAPI(
    title="api swagger",
    version="1.0",
    description="fastapi+tortoise-orm async web framework",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=True,  # 重启服务时自动生成数据库表
    add_exception_handlers=True,
)
# router
app.include_router(user_api, tags=["User"], prefix="/user")
app.include_router(comment_api, tags=["Comment"], prefix="/comment")
# app.include_router(test_route, tags=['Test'], prefix='/test')
# exception
app.add_exception_handler(ResponseException, response_exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """修改默认的请求验证错误模型"""
    return JSONResponse(
        status_code=422, content={"success": False, "detail": exc.errors()}
    )


try:
    scheduler.start()
except:
    log.info("后台任务启动失败！")
else:
    log.info("暂无后台任务！")
