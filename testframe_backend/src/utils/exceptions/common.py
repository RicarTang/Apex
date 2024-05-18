class IncorrectFileError(Exception):
    """无效文件异常"""

    def __init__(self):
        super().__init__("导入的文件无效!")
