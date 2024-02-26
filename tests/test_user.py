import pytest
import faker
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
@pytest.mark.add_user
async def test_user_add_success(client: AsyncClient, login, faker, get_role_list, log):
    """成功添加用户"""
    global new_user_id
    # 种子值为空
    faker.seed_instance(seed=None)
    fake_name = faker.name()
    res = await client.post(
        "/user/add",
        headers={"Authorization": f"Bearer {login}"},
        json=dict(
            userName=fake_name,
            remark="测试添加用户",
            status=1,
            password="123456",
            roleIds=[get_role_list[0]["id"]],
        ),
    )
    new_user_id = res.json()["result"]["id"]
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"
    log.info(f"使用admin用户成功新增用户{fake_name},id:{new_user_id}")


@pytest.mark.anyio
async def test_user_query(client: AsyncClient, login, log):
    """查询某个用户信息"""
    res = await client.get(
        f"/user/{new_user_id}", headers={"Authorization": f"Bearer {login}"}
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "success"
    log.info(f"查询用户id{new_user_id}成功,响应体为:{res.json()}")


@pytest.mark.anyio
async def test_user_resetPwd_success(client: AsyncClient, login, log):
    """成功修改用户密码"""
    new_psw = "12345678"
    res = await client.put(
        "/user/resetPwd",
        headers={"Authorization": f"Bearer {login}"},
        json=dict(userId=new_user_id, password=new_psw),
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "successful reset user password!"
    log.info(f"使用admin用户成功修改用户{new_user_id}的密码为{new_psw}")


@pytest.mark.anyio
async def test_user_update_success(client: AsyncClient, login, get_role_list, log):
    """成功更新用户信息"""
    res = await client.put(
        f"/user/{new_user_id}",
        headers={"Authorization": f"Bearer {login}"},
        json=dict(roleIds=[get_role_list[1]["id"]], status=0, remark="update用户数据"),
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "Update user information successfully!"
    log.info(f"使用admin用户成功更新用户{new_user_id}信息")


@pytest.mark.anyio
async def test_user_del_success(client: AsyncClient, login, log):
    """成功删除用户"""
    url = f"/user/{new_user_id}"
    res = await client.delete(
        url,
        headers={"Authorization": f"Bearer {login}"},
    )
    assert res.status_code == 200
    assert res.json()["success"] == True
    assert res.json()["message"] == "successful deleted user!"
    log.info(f"使用admin用户成功删除用户{new_user_id}")
