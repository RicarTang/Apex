import pickle
import pytest
from ..celery_config import celery
from .....core.cache import RedisService
from .....utils.log_util import log


@celery.task(bind=True)
def task_test(self, testsuite_data: list) -> None:
    """运行pytest测试的task

    Args:
        testsuite_data (list): 接口处传递的测试数据

    Returns:
        _type_: _description_
    """
    log.debug(f"当前task_id:{self.request.id}")
    # 使用task_id为key保存测试数据至redis
    RedisService().set(self.request.id,pickle.dumps(testsuite_data))
    pytest.main(
        [
            "testframe_backend/src/autotest/test_case/test_schema.py::TestApi",
            "-v",
            "--task_id",
            self.request.id,
        ]
    )
    return "Pytest completed."
