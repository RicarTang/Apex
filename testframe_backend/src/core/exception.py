from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from tortoise.exceptions import IntegrityError


async def custom_http_exception_handler(request: Request, exc: HTTPException):
    """自定义的HTTPException

    Args:
        request (Request): _description_
        exc (HTTPException): _description_

    Returns:
        _type_: _description_
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": f"{exc.detail}"},
    )


async def custom_validation_exception_handler(
    request: Request, exc: RequestValidationError
):
    """修改默认的请求验证错误模型

    Args:
        request (Request): _description_
        exc (RequestValidationError): _description_

    Returns:
        _type_: _description_
    """
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": exc.errors()},
    )


# 全局处理数据库Integrity Error
async def custom_integrity_exception_handler(request: Request, exc: IntegrityError):
    # 自定义错误信息
    error_detail = "Integrity Error: Duplicate value or other integrity violation."
    # 返回自定义响应
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": error_detail, "result": str(exc)},
    )
