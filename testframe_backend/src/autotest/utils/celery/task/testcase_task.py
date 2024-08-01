import json, os
import pytest
import subprocess
from .base import BaseTaskWithTest
from ..celery_config import celery
from ....utils.formatter import publish_format
from .....core.redis import RedisService
from .....utils.log_util import log
from .....services.autotest.testsuite import TestSuiteSSEService
from ......config import config


@celery.task(bind=True, name="run_test_task", base=BaseTaskWithTest)
def task_test(self, testsuite_data: list, suite_id: int) -> str:
    """运行pytest测试的task

    Args:
        testsuite_data (list): 接口处传递的测试数据

    Returns:
        str: task结果
    """
    # 报告数据存储目录
    allure_report_dir = config.ALLURE_REPORT / self.request.id
    pytest_data_dir = config.PYTEST_DATA / self.request.id
    # 使用task_id为key保存json格式测试数据至redis
    RedisService().redis_pool().set(self.request.id, json.dumps(testsuite_data))
    exit_code = pytest.main(
        [
            "testframe_backend/src/autotest/test_case/test_factory.py::TestApi",
            "-v",
            "--task_id",
            self.request.id,  # 传递task_id至pytest
            "--alluredir",
            pytest_data_dir,
        ]
    )
    RedisService().redis_pool().publish(self.request.id + "-sse_data", publish_format(f"开始生成allure报告", 0))
    try:
        subprocess.run(
            f"allure generate {pytest_data_dir} -o {allure_report_dir} --clean",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        RedisService().redis_pool().publish(self.request.id + "-sse_data", publish_format(f"生成allure报告失败", 0))
        raise e
    else:
        RedisService().redis_pool().publish(self.request.id + "-sse_data", publish_format(f"生成allure报告成功", 0))
    RedisService().redis_pool().publish(
        self.request.id + "-sse_data",
        publish_format(f"celery 任务 {self.request.id} 完成,测试结束!", 1),
    )
    return exit_code, suite_id
