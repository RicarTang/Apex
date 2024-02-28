import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_case_list(client: AsyncClient, login):
    """获取用例列表"""
    res = await client.get(
        "/testcase/list", headers={"Authorization": f"Bearer {login}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"