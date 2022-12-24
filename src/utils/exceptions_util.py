from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError


# exception_handler
class ResponseException(Exception):
    def __init__(self, content: str):
        self.content = content


# @app.exception_handler(ResponseException)
async def response_exception(request: Request, exc: ResponseException):
    return JSONResponse(
        status_code=200,
        content={
            "success": False,
            "detail": f"{exc.content}"
        }
    )
