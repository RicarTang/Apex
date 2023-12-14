import pickle
from ..core.cache import RedisService
from ..utils.log_util import log


def pytest_addoption(parser):
    """添加pytest命令行选项"""
    parser.addoption(
        "--task_id",
        help="pytest test task id",
    )


def pytest_generate_tests(metafunc):
    """pytest自定义测试用例生成函数,
        测试用例使用suite_id 参数时返回testsuite数据进行参数化

    Args:
        metafunc (_type_): _description_
    """
    if "case" in metafunc.fixturenames:
        # 获取传递过来的当前进程的task_id
        pytest_task_id = metafunc.config.getoption("task_id")
        # redis获取list测试用例
        suite_data = RedisService().getdel(pytest_task_id)
        log.debug(f"pickli后:{pickle.loads(suite_data)}")
        # 用例参数化
        metafunc.parametrize("case", pickle.loads(suite_data))
