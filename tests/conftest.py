import pytest
from pathlib import Path
from asgi_lifespan import LifespanManager
from src.main import app
from httpx import AsyncClient
from loguru import logger


@pytest.fixture(scope="session", name="log")
def _logger():
    """日志夹具"""
    log_directory: Path = Path(__file__).parent / "log"
    log_file = log_directory / "tests_{time:YYYY-MM-DD}.log"
    # 创建一个独立的日志器专门记录单元测试日志
    test_logger = logger.bind(source="unit_test")
    test_logger.add(log_file, level="INFO")
    return logger


@pytest.fixture(scope="session")
def anyio_backend():
    """设置anyio后端为asyncio"""
    return "asyncio"


@pytest.fixture(scope="session")
async def client():
    """配置客户端"""
    async with LifespanManager(app):
        async with AsyncClient(app=app, base_url="http://127.0.0.1:4000") as c:
            yield c


@pytest.fixture(scope="session", autouse=True)
def faker_locale():
    """配置faker local"""
    locale = "zh_CN"
    return locale


@pytest.fixture(scope="session")
async def login(client: AsyncClient):
    """admin用户登录前置"""
    res = await client.post("/login", json=dict(username="admin", password="123456"))
    yield res.json()["result"]["access_token"]


@pytest.fixture(scope="session")
async def get_role_list(client: AsyncClient, login):
    """获取角色列表"""
    res = await client.get(
        "/admin/role/list", headers={"Authorization": f"Bearer {login}"}
    )
    yield res.json()["result"]["data"]
