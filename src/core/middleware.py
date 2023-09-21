import time
import json
from typing import List
from starlette.types import Message
from fastapi import Request
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.middleware.cors import CORSMiddleware
from ..utils.log_util import log


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    日志中间件(继承BaseHTTPMiddleware类方式),
    必须重写dispatch方法;
    """

    async def dispatch(self, request: Request, call_next):
        # log_dict = dict(
        #     method=request.method,
        #     url=request.url,
        #     client_ip=request.client.host,
        #     body=await request.json(),
        # )
        # log.info(f"request info:{log_dict}")
        done = False
        chunks: List[bytes] = []
        receive = request.receive

        async def wrapped_receive() -> Message:  # 取body
            nonlocal done
            message = await receive()
            if message["type"] == "http.disconnect":
                done = True
                return message
            body = message.get("body", b"")
            more_body = message.get("more_body", False)
            if not more_body:
                done = True
            chunks.append(body)
            return message

        request._receive = (
            wrapped_receive  # 赋值给_receive, 达到在call_next使用wrapped_receive的目的
        )
        start_time = time.time()
        response = await call_next(request)
        while not done:
            await wrapped_receive()
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)  # 可以使用response, 添加信息
        body = b"".join(chunks)
        try:
            body = body.decode("utf-8")  # 请求体会有为文件的情况
            body = json.loads(body)
        except:
            pass
        log_dict = dict(
            response_code=response.status_code,
            method=request.method,
            url=request.url,
            client_ip=request.client.host,
            body=body,
        )
        if str(response.status_code).startswith("2") or str(
            response.status_code
        ).startswith("3"):
            log.info(log_dict)
        elif str(response.status_code).startswith("4") or str(
            response.status_code
        ).startswith("5"):
            log.error(log_dict)

        return response


middleware = [
    Middleware(LoggingMiddleware),
    Middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time"],  # 客户端显示自定义请求头
    ),
]
