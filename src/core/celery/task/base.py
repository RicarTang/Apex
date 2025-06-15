from celery import Task
from src.autotest.utils.result_process import ResultProcessor
from src.utils.log_util import log


class BaseTaskWithTest(Task):
    """运行测试任务基类"""

    # 重试参数
    autoretry_for = (TypeError,)
    max_retries = 5
    retry_backoff = True
    retry_backoff_max = 700
    retry_jitter = False

    def before_start(self, task_id, args, kwargs):
        """在任务开始执行之前由工作人员运行"""
        log.info(f"task:{task_id}开始执行,{args},{kwargs}")

    def after_return(self, status, retval, task_id, args, kwargs, einfo):
        """任务返回后调用的处理程序"""
        log.info(
            f"task:{task_id}执行完毕,状态为{status},{args},{kwargs},retval:{retval},einfo:{einfo}"
        )

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """当任务失败时，它由工作人员运行"""
        log.info(f"task:{task_id}执行失败,,{args},{kwargs},exc:{exc},einfo:{einfo}")

    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """当要重试任务时，它由工作线程运行"""
        log.info(f"task:{task_id}准备重试,,{args},{kwargs},exc:{exc},einfo:{einfo}")

    def on_success(self, retval, task_id, args, kwargs):
        """如果任务执行成功，则由工作人员运行"""
        exit_code, suite_id = retval
        log.info(f"task:{task_id}执行成功,pytest退出码:{exit_code},开始修改suite_id:{suite_id}的状态")
        ResultProcessor(exit_code=exit_code, suite_id=suite_id).process_result()
