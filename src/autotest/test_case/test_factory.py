"""测试用例工厂函数模块"""
import pytest
import allure
import httpx
import json
from pytest_assume.plugin import assume
from ...utils.log_util import log


class TestApi:
    # @allure.suite("接口测试集")
    def test_factory(self, current_url: bytes, case: dict):
        """接口测试函数,参数化用例执行

        Args:
            current_url (bytes): 夹具,返回当前测试环境url
            case (dict): 夹具,动态参数化用例
        """
        allure.dynamic.title(case["caseTitle"])  # 添加用例标题
        allure.dynamic.description(case["caseDescription"])  # 添加用例描述
        allure.dynamic.label("owner", case["caseEditor"])  # 添加用例编写者
        allure.dynamic.parameter("body", case["requestParam"])  # 添加测试参数
        allure.dynamic.tag(case["caseModule"])  # 添加用例标签
        # allure.dynamic.severity(case["case_description"])  # 添加用例严重性
        log.info("开始接口请求")
        with httpx.Client(base_url=current_url.decode("utf-8")) as client:
            res: httpx.Response = client.request(
                url=case["apiPath"],
                method=case["apiMethod"],
                # params=dict(page=case),
                json=json.loads(case["requestParam"]),
            )
        log.info(f"接口请求结束，Response：{res.json()}")
        # 断言状态码
        code_assert_res = assume(res.status_code == case["expectCode"])
        log.info(
            f"assert code: {code_assert_res} 实际结果{res.status_code},预期结果{case['expectCode']}"
        )
