import allure, pytest, json
from ..core.redis import RedisService
from ..utils.log_util import log
from ..services.testenv import TestEnvService
from .plugin.sse_plugin import SSEPlugin


def pytest_addoption(parser):
    """添加pytest命令行选项"""
    parser.addoption(
        "--task_id",
        help="pytest test task id",
    )


def pytest_configure(config):
    """Pytest 插件的配置"""
    config.pluginmanager.register(SSEPlugin())


def pytest_generate_tests(metafunc):
    """pytest自定义测试用例生成函数,
        测试用例使用suite_id 参数时返回testsuite数据进行参数化

    Args:
        metafunc (_type_): _description_
    """
    if "case" in metafunc.fixturenames:
        # 获取传递过来的当前进程的task_id
        pytest_task_id = metafunc.config.getoption("task_id")
        # redis获取当前task_id的测试用例
        suite_data = RedisService().redis_pool().getdel(pytest_task_id)
        # 解析待参数化的用例数据
        parametrize_data = json.loads(suite_data)
        # 用例参数化
        metafunc.parametrize("case", parametrize_data)


@pytest.fixture(scope="module", name="current_url")
@allure.step("获取当前环境变量")
def get_currnet_test_url():
    """夹具,获取当前测试环境变量url"""
    current_env = TestEnvService().get_current_env()
    log.info(f"获取当前环境变量,url: {current_env}")
    return current_env
