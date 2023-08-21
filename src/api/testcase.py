# import time
from datetime import datetime
from pathlib import Path
from typing import Optional
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    UploadFile,
    Request,
    Query,
    Response,
    status,
)
from fastapi.responses import FileResponse
from tortoise.exceptions import DoesNotExist
from config import config
from ..schemas import schemas
from ..utils.log_util import log
from ..utils.excel_util import ExcelUtil, save_file

router = APIRouter()


@router.post(
    "/import",
    summary="导入测试用例",
    response_model=schemas.ResultResponse[str],
)
async def add_testcases(response: Response, excel: UploadFile):
    """导入测试用例

    Args:
        excel (UploadFile): excel测试用例

    Returns:
        _type_: _description_
    """
    if excel.filename.endswith(("xlsx", "csv", "xls")):
        # 保存路径
        save_path = (
            config.STATIC_PATH
            / "testcase"
            / "upload"
            / f"{str(datetime.now().strftime('%Y-%m-%d-%H-%M-%S')) + excel.filename}"
        )
        # 保存上传的文件
        save_file(
            file=excel,
            save_path=save_path,
        )
        # 读取表格数据
        wb = ExcelUtil(save_path)
        # 保存testcase到数据库

    else:
        response.status_code = status.HTTP_400_BAD_REQUEST
        schemas.ResultResponse[str](result="template suffix is error!")
    return schemas.ResultResponse[str](result=excel.filename)


@router.get(
    "/template/download",
    summary="下载测试用例excel模板",
)
async def get_testcase_template():
    """下载测试用例excel模板"""
    template: Path = config.STATIC_PATH / "testcase" / "测试用例模板.xlsx"
    if template.exists():
        return FileResponse(template, filename="测试用例模板.xlsx")
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="template is not exise!"
        )


# @router.get("/getAll")
