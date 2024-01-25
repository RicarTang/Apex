import pickle
import pytest
import subprocess
import asyncio
from celery.signals import task_success
from ..celery_config import celery
from ...result_process import ResultProcessor
from .....core.cache import RedisService
from .....utils.log_util import log
from ......config import config


@celery.task(bind=True, name="run_test_task")
def task_test(self, testsuite_data: list) -> str:
    """运行pytest测试的task

    Args:
        testsuite_data (list): 接口处传递的测试数据

    Returns:
        str: task结果
    """
    # 报告数据存储目录
    allure_report_dir = config.ALLURE_REPORT / self.request.id
    pytest_data_dir = config.PYTEST_DATA / self.request.id
    log.debug(f"当前task_id:{self.request.id}")
    log.debug(f"当前测试用例:{testsuite_data}")
    # 使用task_id为key保存测试数据至redis
    RedisService().set(self.request.id, pickle.dumps(testsuite_data))
    exit_code = pytest.main(
        [
            "testframe_backend/src/autotest/test_case/test_factory.py::TestApi",
            "-v",
            "--task_id",
            self.request.id,  # 传递tast_id至pytest
            "--alluredir",
            pytest_data_dir,
        ]
    )
    log.debug(f"测试退出码：{exit_code}")
    try:
        subprocess.run(
            f"allure generate {pytest_data_dir} -o {allure_report_dir} --clean",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise e
    return exit_code


# @task_success.connect
# def test_callback(result, suite_id):
#     """测试任务执行完成后的回调函数"""
#     log.debug(f"执行了回调函数,{result, suite_id}")
#     asyncio.run(ResultProcessor(exit_code=result, suite_id=suite_id).process_result())
@celery.task()
def test_callback(result, suite_id):
    """测试任务执行完成后的回调函数"""
    log.debug(f"测试退出码:{result},修改suite_id:{suite_id}的状态")
    ResultProcessor(exit_code=result, suite_id=suite_id).process_result()
