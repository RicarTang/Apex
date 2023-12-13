import pickle

def pytest_addoption(parser):
    """添加pytest命令行选项"""
    parser.addoption(
        "--suite_data",
        help="test suite id",
    )


def pytest_generate_tests(metafunc):
    """pytest自定义测试用例生成函数,
        测试用例使用suite_id 参数时返回testsuite数据进行参数化

    Args:
        metafunc (_type_): _description_
    """
    if "case" in metafunc.fixturenames:
        suite_data = metafunc.config.getoption("suite_data")
        metafunc.parametrize("case", pickle.loads(suite_data))
