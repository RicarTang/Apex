import pytest,time,requests
from ..services.testenv_service import TestEnvService


class TestApi:

    @classmethod
    def setup_class(cls,):
        cls.testenv = TestEnvService()

    @pytest.mark.asyncio
    # @pytest.mark.parametrize("data",[112,222])
    async def test_demo(self):
        # res = requests.request(url=await self.depend.get_current_env+data["api_path"],method=data["api_method"])
        print(await self.testenv.get_current_env)
        res = requests.request(url="http://127.0.0.1:4000/testenv/getAll",method="get")
        assert res.status_code == 200