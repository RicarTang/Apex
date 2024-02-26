import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_role_list(client: AsyncClient, login):
    """获取角色列表"""
    res = await client.get(
        "/admin/role/list", headers={"Authorization": f"Bearer {login}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"


@pytest.mark.anyio
async def test_permission_list(client: AsyncClient, login):
    """获取权限列表"""
    res = await client.get(
        "/admin/permission/list", headers={"Authorization": f"Bearer {login}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"
