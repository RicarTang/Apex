"""文件读取"""
import json,yaml, aiofiles
from typing import Any, Dict


class File:
    """操作文件类"""

    @staticmethod
    async def loadjson(file_path: str) -> dict:
        """
        读取json文件并返回解析后的字典。

        Args:
            file_path (str): JSON 文件的路径。

        Returns:
            dict: 解析后的 JSON 数据。
        """
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                data = json.load(await file.read())
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Error decoding JSON in file {file_path}: {e}")

    @staticmethod
    async def loadyaml(file_path: str) -> dict:
        """
        读取 YAML 文件并返回解析后的数据。

        Args:
            file_path (str): YAML 文件的路径。

        Returns:
            dict: 解析后的 YAML 数据。
        """
        try:
            async with aiofiles.open(file_path, "r", encoding="utf-8") as file:
                data = yaml.load(await file.read(), Loader=yaml.FullLoader)
            return data
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML in file {file_path}: {e}")

    @staticmethod
    async def append_to_yaml(file_path: str, data_to_append: Dict[str, Any]) -> None:
        """
        异步追加写入 YAML 文件。

        Args:
            file_path (str): YAML 文件的路径。
            data_to_append (dict): 要追加写入的数据。

        Returns:
            None
        """
        try:
            async with aiofiles.open(file_path, "a+", encoding="utf-8") as file:
                # 写入追加的数据
                await file.write(yaml.dump(data_to_append, default_flow_style=False))
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {file_path}")
        except (yaml.YAMLError, Exception) as e:
            raise ValueError(f"Error appending to YAML file {file_path}: {e}")


if __name__ == "__main__":
    import asyncio
    from pathlib import Path

    path = Path(__file__).parent.parent / "autotest" / "config" / "config.yaml"

    async def main():
        # return await File.loadyaml(path)
        await File.append_to_yaml(path, {"sregdfgtr": 2})

    print(asyncio.run(main()))
