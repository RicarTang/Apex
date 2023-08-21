from pathlib import Path
from fastapi import UploadFile
from openpyxl import load_workbook, Workbook


class ExcelUtil:
    """excel工具类"""

    def __init__(self, filename: str) -> None:
        self.wb: Workbook = load_workbook(filename)

    def read_all(self) -> list:
        """读取excel所有数据"""
        # 获取所有sheet
        sheets = self.wb.sheetnames
        testcases = []  # 存放所有读取的testcase
        # 遍历每个sheet的所有数据
        for sheetname in sheets:
            sheet = self.wb[sheetname]
            # 使用列表推导式生成单个sheet的testcase
            testcase = [item for item in sheet.values][1:]
            # 使用 extend() 将单个sheet的testcase合并到总的testcases列表中
            testcases.extend(testcase)
        return testcases

    def append_write(self):
        """追加写入excel"""
        pass

    def cover_write(self):
        """覆盖写入excel"""
        pass


def save_file(file: UploadFile, save_path: Path) -> None:
    """保存上传的文件

    Args:
        file (bytes):  二进制文件
        save_path (Path): 保存的路径
    """
    # 获取文件对象
    uploaded_file = file.file
    # 将文件内容写入目标文件
    with open(save_path, "wb") as f:
        # 避免一次读取内存过大
        while chunk := uploaded_file.read(8192):
            f.write(chunk)


if __name__ == "__main__":
    path = Path(__file__)
    ex = path.parent.parent.parent / "static/testcase/测试用例模板.xlsx"
    excel = ExcelUtil(ex)
    data = excel.read_all()
    print(data)
