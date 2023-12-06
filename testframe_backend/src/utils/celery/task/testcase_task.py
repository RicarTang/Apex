from ..celery_config import celery
import time


@celery.task
def run_pytest():
    print("Running pytest...")
    time.sleep(10)
    return "Pytest completed."