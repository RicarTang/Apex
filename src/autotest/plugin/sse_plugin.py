import os
from ...utils.log_util import log
from ...core.redis import RedisService
from ..utils.formatter import publish_format


class SSEPlugin:
    """Pytest 插件类"""
    test_results = {"passed": 0, "failed": 0, "skipped": 0}

    def pytest_sessionstart(self, session):
        # 在测试会话开始时初始化测试结果统计
        RedisService().redis_pool.publish(
            session.config.getoption("task_id") + "-sse_data",
            publish_format(
                f"开始启动pytest会话,task id为{session.config.getoption('task_id')}", 0
            ),
        )
        self.test_results = {"passed": 0, "failed": 0, "skipped": 0}
        log.debug(f"测试环境pid：{os.getpid()}")

    def pytest_runtest_protocol(self, item, nextitem):
        # 在每个测试用例执行前更新测试结果统计
        log.debug(f"开始执行用例 {item.name}")
        RedisService().redis_pool.publish(
            item.config.getoption("task_id") + "-sse_data",
            publish_format(f"开始执行用例 {item.name}", 0),
        )

    def pytest_runtest_logreport(self, report):
        # 在每个测试用例执行后更新测试结果统计
        log.debug(report)
        if report.when == "call":
            if report.passed:
                self.test_results["passed"] += 1
            elif report.failed:
                self.test_results["failed"] += 1
            elif report.skipped and hasattr(report, "wasxfail"):
                self.test_results["failed"] += 1
            elif report.skipped:
                self.test_results["skipped"] += 1

    def pytest_sessionfinish(self, session, exitstatus):
        """在整个测试运行完成后、将退出状态返回给系统之前调用"""
        RedisService().redis_pool.publish(
            session.config.getoption("task_id") + "-sse_data",
            publish_format(
                f"pytest会话结束,测试结果: {self.test_results},退出码: {exitstatus}", 0
            ),
        )
