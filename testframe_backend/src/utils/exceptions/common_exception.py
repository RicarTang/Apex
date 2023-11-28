class IncorrectFileError(Exception):
    """无效文件异常"""

    def __init__(self):
        super().__init__("Invalid file imported!")
