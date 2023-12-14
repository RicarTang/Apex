"""测试用例工厂函数模块"""
import pytest
import allure
import httpx
from ...services.testenv_service import TestEnvService
from ...utils.log_util import log


class TestApi:
    @pytest.fixture(scope="class", name="current_url")
    @allure.title("获取当前环境变量")
    def get_currnet_test_url(self):
        """夹具,获取当前测试环境变量url"""
        return TestEnvService().get_current_env()

    # @allure.suite()
    def test_factory(self, current_url, case):
        """接口测试函数

        Args:
            current_url (_type_): 当前环境变量
            data (_type_): 测试用例列表
        """
        allure.dynamic.title(case["case_title"])  # 添加用例标题
        allure.dynamic.description(case["case_description"])  # 添加用例描述
        allure.dynamic.label("owner", case["case_editor"])  # 添加用例编写者
        # allure.dynamic.parameter()
        # allure.dynamic.severity(case["case_description"])  # 添加用例严重性
        with httpx.Client(base_url=current_url.decode("utf-8")) as client:
            res = client.request(
                url="/testenv/getAll",
                method="get",
                # params=dict(page=case),
            )
        assert res.status_code == 200
