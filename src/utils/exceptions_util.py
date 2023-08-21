from fastapi import Request,HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError



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
        content={
            "code": exc.status_code,
            "message": f"{exc.detail}"
        }
    )
