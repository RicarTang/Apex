import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_login_success(client: AsyncClient):
    """登录成功测试"""
    res = await client.post("/login", json=dict(username="admin", password="123456"))
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"


@pytest.mark.anyio
async def test_login_password_error(client: AsyncClient):
    """密码错误登录"""
    res = await client.post("/login", json=dict(username="admin", password="123456789"))
    assert res.status_code == 403
    assert res.json()["success"] == False
    assert res.json()["message"] == "Password validate error!"


@pytest.mark.anyio
async def test_login_password_lt_6(client: AsyncClient):
    """密码小于6个字符登录"""
    res = await client.post("/login", json=dict(username="admin", password="12345"))
    assert res.status_code == 422
    assert res.json()["success"] == False
    assert res.json()["message"][0]["type"] == "string_too_short"
    assert res.json()["message"][0]["msg"] == "String should have at least 6 characters"


@pytest.mark.anyio
async def test_login_user_does_not_exist(client: AsyncClient):
    """用户不存在登录登录"""
    res = await client.post("/login", json=dict(username="kdsfd", password="123456"))
    assert res.status_code == 404
    assert res.json()["success"] == False
    assert res.json()["message"] == "User does not exist!"


@pytest.mark.anyio
async def test_login_username_is_empty(client: AsyncClient):
    """username为空登录"""
    res = await client.post("/login", json=dict(username="", password="123456"))
    assert res.status_code == 422
    assert res.json()["success"] == False


@pytest.mark.anyio
async def test_login_password_is_empty(client: AsyncClient):
    """password为空登录"""
    res = await client.post("/login", json=dict(username="admin", password=""))
    assert res.status_code == 422
    assert res.json()["success"] == False


@pytest.mark.anyio
async def test_login_missing_username(client: AsyncClient):
    """缺少username登录"""
    res = await client.post("/login", json=dict(password="123456"))
    assert res.status_code == 422
    assert res.json()["success"] == False


@pytest.mark.anyio
async def test_login_missing_password(client: AsyncClient):
    """缺少password登录"""
    res = await client.post("/login", json=dict(username="admin"))
    assert res.status_code == 422
    assert res.json()["success"] == False
