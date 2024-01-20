import pytest
from asgi_lifespan import LifespanManager
from testframe_backend.main import app
from httpx import AsyncClient


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio" 


@pytest.fixture(scope="module")
async def client():
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://127.0.0.1:4000") as c:
            yield c