import sys, os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from .src.api import (
    user_api,
    admin_api,
    # testcase_api,
    # testsuite_api,
    # testenv_api,
    # config_api,
    default_api,
    # menu_api,
)
from .src.core.security import check_jwt_auth
from .src.core.middleware import middleware
from .src.core.exception import (
    custom_http_exception_handler,
    custom_validation_exception_handler,
    # custom_integrity_exception_handler,
)
from .config import config
from .src.utils.log_util import log
# from .src.db import InitDbData


app = FastAPI(
    title="api swagger",
    version="1.0",
    description="fastapi+tortoise-orm async web framework",
    middleware=middleware,  # 注册middleware
    docs_url=None,  # docs url设置为none，使用自定义的docs路由
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

    # # 初始化数据库,需要在注册tortoise后面初始化
    # await InitDbData().execute_init()


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """自定义swagger"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + "- Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )



# include router
app.include_router(default_api)  # default
app.include_router(
    user_api,
    tags=["User"], 
    prefix="/user",
    # dependencies=[Depends(check_jwt_auth)],
)
app.include_router(
    admin_api,
    tags=["Admin"],
    prefix="/admin",
    # dependencies=[Depends(check_jwt_auth)],
)
# app.include_router(
#     testcase_api,
#     tags=["Testcase"],
#     prefix="/testcase",
#     # dependencies=[Depends(check_jwt_auth)],
# )
# app.include_router(
#     testsuite_api,
#     tags=["Testsuite"],
#     prefix="/testsuite",
#     # dependencies=[Depends(check_jwt_auth)],
# )
# app.include_router(
#     testenv_api,
#     tags=["TestEnvironment"],
#     prefix="/testenv",
#     # dependencies=[Depends(check_jwt_auth)],
# )
# app.include_router(
#     config_api,
#     tags=["Config"],
#     prefix="/config",
#     # dependencies=[Depends(check_jwt_auth)],
# )
# app.include_router(
#     menu_api,
#     tags=["Menu"],
#     prefix="/menu",
#     # dependencies=[Depends(check_jwt_auth)],
# )


# 注册自定义的exception
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_exception_handler(RequestValidationError, custom_validation_exception_handler)
# app.add_exception_handler(IntegrityError, custom_integrity_exception_handler)

