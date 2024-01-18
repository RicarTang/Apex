import pytest
from httpx import AsyncClient


# @pytest.mark.endpoint
@pytest.mark.asyncio
async def test_login_success():
    """登录成功测试"""
    async with AsyncClient(base_url="http://127.0.0.1:4000") as client:
        res = await client.post(
            "/user/login", json=dict(username="admin", password="123456")
        )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"


# @pytest.mark.endpoint
@pytest.mark.asyncio
async def test_login_password_error():
    """密码错误登录"""
    async with AsyncClient(base_url="http://127.0.0.1:4000") as client:
        res = await client.post(
            "/user/login", json=dict(username="admin", password="12345")
        )
    assert res.status_code == 422
    assert res.json()["success"] == False
