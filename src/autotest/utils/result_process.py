from sqlalchemy import text
from ...utils.sql_engine import engine
from ...utils.log_util import log


class ResultProcessor:
    """pytest exit code反射类"""

    def __init__(self, exit_code: int, suite_id: int) -> None:
        self.exit_code = exit_code
        self.suite_id = suite_id

    def process_result(self):
        """处理反射方法"""
        method_name = f"process_result_{self.exit_code}"
        method = getattr(self, method_name)
        method()

    def process_result_0(self) -> int:
        """Tests passed"""
        log.info(f"更新suite_id:{self.suite_id}状态为1")
        sql = text("UPDATE test_suite SET status = :status WHERE id = :suite_id")
        with engine.connect() as con:
            res = con.execute(sql, dict(status=1, suite_id=self.suite_id))
            con.commit()
            return res.rowcount

    def process_result_1(self) -> int:
        """Tests failed"""
        log.info(f"更新suite_id:{self.suite_id}状态为2")
        sql = text("UPDATE test_suite SET status = :status WHERE id = :suite_id")
        with engine.connect() as con:
            res = con.execute(sql, dict(status=2, suite_id=self.suite_id))
            con.commit()
            return res.rowcount

    def process_result_2(self):
        """pytest was interrupted"""
        pass

    def process_result_3(self):
        """An internal error got in the way"""
        pass

    def process_result_4(self):
        """pytest was misused"""
        pass

    def process_result_5(self):
        """pytest couldn't find tests"""
        pass
