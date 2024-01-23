import pytest
from asgi_lifespan import LifespanManager
from testframe_backend.main import app
from httpx import AsyncClient


@pytest.fixture(scope="module")
def anyio_backend():
    """设置anyio后端为asyncio"""
    return "asyncio"


@pytest.fixture(scope="module")
async def client():
    """配置客户端"""
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://127.0.0.1:4000") as c:
            yield c


@pytest.fixture(scope="module")
async def login(client: AsyncClient):
    """登录前置"""
    res = await client.post("/login", json=dict(username="admin", password="123456"))
    yield res.json()["result"]["access_token"]


@pytest.fixture(scope="module")
async def get_role_list(client: AsyncClient, login):
    """获取角色列表"""
    res = await client.get(
        "/admin/role/list", headers={"Authorization": f"Bearer {login}"}
    )
    yield res.json()["result"]["data"]
