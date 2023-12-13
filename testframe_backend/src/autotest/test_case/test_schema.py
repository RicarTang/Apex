"""测试用例工厂函数模块"""
import asyncio
import pytest
import httpx
from ...services.testenv_service import TestEnvService


class TestApi:
    @pytest.fixture(scope="class", name="current_url")
    def get_currnet_test_url(self):
        """夹具,获取当前测试环境变量url"""
        return asyncio.run(TestEnvService.get_current_env())

    @pytest.mark.asyncio
    async def test_factory(self, current_url, case):
        """接口测试函数

        Args:
            current_url (_type_): 当前环境变量
            data (_type_): 测试用例列表
        """
        
        print("测试套件id",case)
        async with httpx.AsyncClient(base_url=current_url) as client:
            res = await client.request(
                url="/testenv/getAll",
                method="get",
                # params=dict(page=case),
            )
            assert res.status_code == 200
