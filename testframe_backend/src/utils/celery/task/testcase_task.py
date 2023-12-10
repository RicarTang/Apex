from ..celery_config import celery
import time, pytest

@celery.task
def run_pytest():
    print("Running pytest...")
    time.sleep(10)
    return "Pytest completed."


@celery.task
def task_test():
    pytest.main(["testframe_backend/src/autotest/test_schema.py::TestApi"])
    return "Pytest completed."