import pickle
import pytest
import os
import subprocess
from pathlib import Path
from ..celery_config import celery
from .....core.cache import RedisService
from .....utils.log_util import log
from ......config import config


@celery.task(bind=True)
def task_test(self, testsuite_data: list) -> None:
    """运行pytest测试的task

    Args:
        testsuite_data (list): 接口处传递的测试数据

    Returns:
        _type_: _description_
    """
    # 报告数据存储目录
    # allure_report_dir = config.TEST_PATH / "report" / self.request.id / "allure_report"
    # pytest_data_dir = config.TEST_PATH / "report" / self.request.id / "pytest_data"
    allure_report_dir = config.ALLURE_REPORT / self.request.id
    pytest_data_dir = config.PYTEST_DATA / self.request.id
    log.debug(f"当前task_id:{self.request.id}")
    # 使用task_id为key保存测试数据至redis
    RedisService().set(self.request.id, pickle.dumps(testsuite_data))
    pytest.main(
        [
            "testframe_backend/src/autotest/test_case/test_factory.py::TestApi",
            "-v",
            "--task_id",
            self.request.id,
            "--alluredir",
            pytest_data_dir,
        ]
    )
    try:
        subprocess.run(
            f"allure generate {pytest_data_dir} -o {allure_report_dir} --clean",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        raise e
    # os.system(
    #     f"allure generate {pytest_data_dir} -o {allure_report_dir} --clean"
    # )
    return "Pytest completed."
