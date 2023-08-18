from pathlib import Path
from openpyxl import load_workbook


class ExcelUtil:
    """excel工具类"""
    def __init__(self, filename: str) -> None:
        self.wb = load_workbook(filename)

    def read_all(self) -> None:
        """读取excel所有数据"""

        return self.wb.rows

    def append_write(self):
        """追加写入excel"""
        pass

    def cover_write(self):
        """覆盖写入excel"""
        pass



if __name__ == '__main__':
    path = Path(__file__).resolve()
    ex = path.parent.parent.parent / "static/testcase/测试用例模板.xlsx"
    print(ex.exists())
    excel = ExcelUtil(path.parent.parent.parent / "static/testcase/测试用例模板.xlsx")
    # rows = excel.read_all()
    # print(rows)