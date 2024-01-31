import sys, os
# from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from tortoise.exceptions import IntegrityError
from tortoise.contrib.fastapi import register_tortoise
from .src.api import (
    user_api,
    admin_api,
    testcase_api,
    testsuite_api,
    testenv_api,
    config_api,
    default_api,
    menu_api,
)
from .src.core.security import check_jwt_auth
from .src.core.middleware import middleware
from .src.core.exception import (
    custom_http_exception_handler,
    custom_validation_exception_handler,
    custom_integrity_exception_handler,
)
from .config import config

# from .src.core.cache import init_cache
# from .src.utils.background_task_util import scheduler
from .src.utils.log_util import log
from .src.db.settings import TORTOISE_ORM
from .src.db import InitDbData


app = FastAPI(
    title="api swagger",
    version="1.0",
    description="fastapi+tortoise-orm async web framework",
    middleware=middleware,  # 注册middleware
)

# 注册tortoise orm 需要在initial_data前面
register_tortoise(
    app,
    config=TORTOISE_ORM,
    generate_schemas=False,  # 重启服务时自动生成数据库表；关闭，改为使用aerich
    add_exception_handlers=True,
)


@app.on_event("startup")
async def lifespan():
    """fastapi初始化"""
    # 初始化缓存池
    # await init_cache()
    # 挂载静态文件
    # swagger 静态文件
    app.mount(
        "/static",
        StaticFiles(packages=[("testframe_backend", "static")]),
        name="static",
    )
    # allure报告
    if config.ON_STATICFILES:
        try:
            app.mount(
                "/report",
                StaticFiles(directory=config.ALLURE_REPORT, html=True),
                name="report",
            )
        except RuntimeError:
            os.makedirs(config.ALLURE_REPORT)

    # 初始化数据库,需要在注册tortoise后面初始化
    await InitDbData().execute_init()
    # 修改默认swagger参数，使用static文件
    sys.modules["fastapi.applications"].get_swagger_ui_html.__kwdefaults__[
        "swagger_js_url"
    ] = "/static/swagger-ui/swagger-ui-bundle.js"
    sys.modules["fastapi.applications"].get_swagger_ui_html.__kwdefaults__[
        "swagger_css_url"
    ] = "/static/swagger-ui/swagger-ui.css"


# 注册CORS中间件(迁移至core.middleware模块)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
#     expose_headers=["X-Process-Time"],  # 浏览器显示自定义请求头
# )
# app.add_middleware(TimeMiddleware)

# 自定义中间件(函数方式)
# @app.middleware("http")
# async def custom_time_header(request: Request, call_next):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     response.headers["X-Process-Time"] = str(process_time)
#     return response


# include router
app.include_router(default_api)  # default
app.include_router(
    user_api,
    tags=["User"],
    prefix="/user",
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
app.include_router(
    testsuite_api,
    tags=["Testsuite"],
    prefix="/testsuite",
    # dependencies=[Depends(check_jwt_auth)],
)
app.include_router(
    testenv_api,
    tags=["TestEnvironment"],
    prefix="/testenv",
    # dependencies=[Depends(check_jwt_auth)],
)
app.include_router(
    config_api,
    tags=["Config"],
    prefix="/config",
    # dependencies=[Depends(check_jwt_auth)],
)
app.include_router(
    menu_api,
    tags=["Menu"],
    prefix="/menu",
    # dependencies=[Depends(check_jwt_auth)],
)


# 注册自定义的exception(方式一)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
app.add_exception_handler(IntegrityError, custom_integrity_exception_handler)

# 注册自定义的exception(方式二)
# @app.exception_handler(RequestValidationError)
# async def custom_validation_exception_handler(
#     request: Request, exc: RequestValidationError
# ):
#     """修改默认的请求验证错误模型"""
#     return JSONResponse(status_code=422, content={"code": 400, "message": exc.errors()})


# try:
#     scheduler.start()
# except:
#     log.info("后台任务启动失败！")
# else:
#     log.info("暂无后台任务！")
