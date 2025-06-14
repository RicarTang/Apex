"""项目入口文件"""

import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_swagger_ui_html
from tortoise.exceptions import IntegrityError
from src.controllers import (
    user_api,
    admin_api,
    testcase_api,
    testsuite_api,
    testenv_api,
    config_api,
    default_api,
    menu_api,
)
from src.core.security import check_jwt_auth
from src.core.middleware import middleware
from src.core.exception import (
    custom_http_exception_handler,
    custom_validation_exception_handler,
    custom_integrity_exception_handler,
)
from src.core.db import register_db
from .config import config
from src.db import InitDbData


app = FastAPI(
    title=config.SWAGGER_TITLE,
    version=config.SWAGGER_VERSION,
    description=config.SWAGGER_DES,
    middleware=middleware,  # 注册middleware
    docs_url=None,  # docs url设置为none，使用自定义的docs路由
)

# 注册tortoise orm 需要在initial_data前面
register_db(app)


@app.on_event("startup")
async def lifespan():
    """fastapi初始化"""
    # 挂载静态文件
    # swagger 静态文件
    app.mount(
        "/static",
        StaticFiles(directory=config.STATIC_PATH),
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

    # 初始化用户角色数据,需要在注册tortoise后面初始化
    await InitDbData().execute_init()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义swagger"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + "- Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url=config.SWAGGER_JS_URL,
        swagger_css_url=config.SWAGGER_CSS_URL,
        swagger_favicon_url=config.SWAGGER_FAVICON_URL,
    )


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


# 注册自定义的exception
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
app.add_exception_handler(IntegrityError, custom_integrity_exception_handler)
