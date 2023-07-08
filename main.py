from fastapi import FastAPI, Request, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from src.api import user_api, comment_api, admin_api
from src.utils.exceptions_util import ResponseException, response_exception
from src.utils.background_task_util import scheduler
from src.utils.log_util import log
from src.db.settings import TORTOISE_ORM
from src.core.security import check_jwt_auth

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
    generate_schemas=False,  # 重启服务时自动生成数据库表；关闭，改为使用aerich
    add_exception_handlers=True,
)
# router
app.include_router(user_api, tags=["User"], prefix="/user")
app.include_router(comment_api, tags=["Comment"], prefix="/comment",dependencies=[Depends(check_jwt_auth)])
app.include_router(admin_api, tags=["Admin"], prefix="/admin",dependencies=[Depends(check_jwt_auth)])

# 注册exception
app.add_exception_handler(ResponseException, response_exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """修改默认的请求验证错误模型"""
    return JSONResponse(
        status_code=422, content={"code": 400, "message": exc.errors()}
    )


try:
    scheduler.start()
except:
    log.info("后台任务启动失败！")
else:
    log.info("暂无后台任务！")

@app.get('/demo')
def demo():
    print("dsfk")