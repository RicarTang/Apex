from fastapi import APIRouter, Request
from starlette.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse
import asyncio
from ..utils.log_util import log


router = APIRouter()


async def generate_data(request: Request):
    while True:
        if await request.is_disconnected():
            log.debug("Request disconnected")
            break
        yield {"event": "update", "retry": 1000, "data": {"message": "demo"}}
        await asyncio.sleep(1)  # 模拟耗时操作


@router.get("/demo")
async def sse_demo(request: Request):
    return EventSourceResponse(generate_data(request))
