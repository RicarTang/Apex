import json, os
import pytest
import subprocess
from .base import BaseTaskWithTest
from ..celery_app import celery
from src.autotest.utils.formatter import publish_format
from src.core.redis import RedisService
from src.utils.log_util import log
from src.services.autotest.testsuite import TestSuiteSSEService
from src.config import config


@celery.task(bind=True, name="run_test_task", base=BaseTaskWithTest)
def task_test(self, testsuite_data: list, suite_id: int) -> tuple:
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
    RedisService().redis_pool.set(self.request.id, json.dumps(testsuite_data))
    exit_code = pytest.main(
        [
            "src/autotest/test_case/test_factory.py::TestApi",
            "-v",
            "--task_id",
            self.request.id,  # 传递task_id至pytest
            "--alluredir",
            pytest_data_dir,
        ]
    )
    RedisService().redis_pool.publish(
        self.request.id + "-sse_data", publish_format("开始生成allure报告", 0)
    )
    try:
        subprocess.run(
            f"allure generate {pytest_data_dir} -o {allure_report_dir} --clean",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError as e:
        RedisService().redis_pool.publish(
            self.request.id + "-sse_data", publish_format("生成allure报告失败", 0)
        )
        raise e
    else:
        RedisService().redis_pool.publish(
            self.request.id + "-sse_data", publish_format("生成allure报告成功", 0)
        )
    RedisService().redis_pool.publish(
        self.request.id + "-sse_data",
        publish_format(f"celery 任务 {self.request.id} 完成,测试结束!", 1),
    )
    return exit_code, suite_id
