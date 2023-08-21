import sys
from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from src.api import user_api, comment_api, admin_api, testcase_api
from src.utils.exceptions_util import ResponseException, response_exception
from src.utils.background_task_util import scheduler
from src.utils.log_util import log
from src.db.settings import TORTOISE_ORM
from src.core.security import check_jwt_auth
from src.db import create_initial_users
from src.core.cache import init_redis_pool

app = FastAPI(
    title="api swagger",
    version="1.0",
    description="fastapi+tortoise-orm async web framework",
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.on_event("startup")
def use_local_swagger_static():
    """修改默认swagger参数"""
    sys.modules["fastapi.applications"].get_swagger_ui_html.__kwdefaults__[
        "swagger_js_url"
    ] = "/static/swagger-ui/swagger-ui-bundle.js"
    sys.modules["fastapi.applications"].get_swagger_ui_html.__kwdefaults__[
        "swagger_css_url"
    ] = "/static/swagger-ui/swagger-ui.css"


@app.on_event("startup")
async def redis_pool():
    """初始化cache"""
    await init_redis_pool()


# 注册CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册tortoise
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # 重启服务时自动生成数据库表；关闭，改为使用aerich
    add_exception_handlers=True,
)


@app.on_event("startup")
async def create_initial_users_roles():
    """创建默认用户角色,需要在注册tortoise后面初始化默认用户"""
    await create_initial_users()


# router
app.include_router(user_api, tags=["User"], prefix="/user")
app.include_router(
    comment_api,
    tags=["Comment"],
    prefix="/comment",
    dependencies=[Depends(check_jwt_auth)],
)
app.include_router(
    admin_api,
    tags=["Admin"],
    prefix="/admin",
    dependencies=[Depends(check_jwt_auth)],
)
app.include_router(
    testcase_api,
    tags=["Testcase"],
    prefix="/testcase",
    # dependencies=[Depends(check_jwt_auth)],
)


# 注册exception
app.add_exception_handler(ResponseException, response_exception)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """修改默认的请求验证错误模型"""
    return JSONResponse(status_code=422, content={"code": 400, "message": exc.errors()})


try:
    scheduler.start()
except:
    log.info("后台任务启动失败！")
else:
    log.info("暂无后台任务！")
