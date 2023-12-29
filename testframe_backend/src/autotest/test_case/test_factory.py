"""测试用例工厂函数模块"""
import pytest
import allure
import httpx
import json
from pytest_assume.plugin import assume
from ...services.testenv import TestEnvService
from ...utils.log_util import log


class TestApi:
    @pytest.fixture(scope="class", name="current_url")
    @allure.title("获取当前环境变量")
    def get_currnet_test_url(self):
        """夹具,获取当前测试环境变量url"""
        log.info("获取当前环境变量")
        return TestEnvService().get_current_env()

    # @allure.suite("接口测试集")
    def test_factory(self, current_url: bytes, case: list):
        """接口测试函数,参数化用例执行

        Args:
            current_url (bytes): 夹具,返回当前测试环境url
            case (list): 夹具,返回测试用例集
        """
        allure.dynamic.title(case["case_title"])  # 添加用例标题
        allure.dynamic.description(case["case_description"])  # 添加用例描述
        allure.dynamic.label("owner", case["case_editor"])  # 添加用例编写者
        allure.dynamic.parameter("body",case["request_param"])  # 添加测试参数
        allure.dynamic.tag(case["case_module"])  # 添加用例标签
        # allure.dynamic.severity(case["case_description"])  # 添加用例严重性
        log.info("开始接口请求")
        with httpx.Client(base_url=current_url.decode("utf-8")) as client:
            res: httpx.Response = client.request(
                url=case["api_path"],
                method=case["api_method"],
                # params=dict(page=case),
                json=json.loads(case["request_param"])
            )
        log.info(f"接口请求结束，Response：{res.json()}")
        # 断言状态码
        code_assert_res = assume(res.status_code == case["expect_code"])
        log.info(f"assert code: {code_assert_res} 实际结果{res.status_code},预期结果{case['expect_code']}")
