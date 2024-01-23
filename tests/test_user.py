import pytest
from faker import Faker
from httpx import AsyncClient


@pytest.mark.anyio
async def test_user_list(client: AsyncClient, login):
    """获取用户列表"""
    res = await client.get("/user/list", headers={"Authorization": f"Bearer {login}"})
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"


@pytest.mark.anyio
async def test_user_me(client: AsyncClient, login):
    """获取当前用户信息"""
    res = await client.get("/user/me", headers={"Authorization": f"Bearer {login}"})
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"


@pytest.mark.anyio
async def test_user_add_success(client: AsyncClient, login, faker, get_role_list):
    """成功添加用户"""
    res = await client.post(
        "/user/add",
        headers={"Authorization": f"Bearer {login}"},
        json=dict(
            userName=faker.name(),
            remark="测试添加用户",
            status=1,
            password="123456",
            roleIds=[get_role_list[0]["id"]],
        ),
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"
