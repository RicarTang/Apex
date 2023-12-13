from ..celery_config import celery
import pytest
import pickle
import json


@celery.task
def task_test(testsuite_data: bytes):
    """运行pytest测试的task

    Args:
        testsuite_data (list): 接口处传递的测试数据

    Returns:
        _type_: _description_
    """
    pytest.main(
        [
            "testframe_backend/src/autotest/test_case/test_schema.py::TestApi",
            "-v",
            "--suite_id",
            testsuite_data,
        ]
    )  # @TODO 添加options，存放suite_id?
    return "Pytest completed."
