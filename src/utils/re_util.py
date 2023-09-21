import re


def serach_filename(data: str) -> str:
    """提取请求体body的二进制文件中的filename

    Args:
        data (str): 请求体二进制字符串

    Returns:
        str: _description_
    """
    # 使用正则表达式提取包括filename=在内的部分
    filename_match = re.search(br'filename="([^"]+)"', data)

    # 如果找到匹配，提取整个匹配的部分
    if filename_match:
        filename_with_prefix = filename_match.group(0)
        return filename_with_prefix.decode("utf-8")
    else:
        return "导入了未知的文件名"
