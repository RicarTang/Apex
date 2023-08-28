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
from config import config
from ..crud import TestCaseDao
from ..schemas import ResultResponse, testcase_schema
from ..utils.log_util import log
from ..utils.excel_util import save_file, read_all_testcase

router = APIRouter()


@router.post(
    "/add",
    summary="添加测试用例",
    response_model=ResultResponse[testcase_schema.TestCaseTo],
)
async def add_testcase(body: testcase_schema.TestCaseIn):
    """添加单条测试用例到数据库

    Args:
        body (testcase_schema.TestCaseIn): _description_


    Returns:
        _type_: _description_
    """
    result = await TestCaseDao.add_testcase(body.dict())
    return ResultResponse[testcase_schema.TestCaseTo](result=result)


@router.post(
    "/import",
    summary="导入excel测试用例",
    response_model=ResultResponse[str],
)
async def add_testcases(response: Response, excel: UploadFile):
    """导入测试用例

    Args:
        excel (UploadFile): excel测试用例

    Returns:
        _type_: _description_
    """
    if excel.filename.endswith(("xlsx", "csv", "xls")):
        # 保存文件名
        save_name = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + excel.filename
        # 保存路径
        save_path = config.STATIC_PATH / "testcase" / "upload" / save_name
        # 保存上传的文件
        await save_file(
            file=excel,
            save_path=save_path,
        )
        # 读取表格数据
        testcase_list = await read_all_testcase(save_path)
        log.debug(f"testcase_list:{testcase_list}")
        # 保存testcase到数据库

    else:
        # 上传文件格式错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="template suffix is error!"
        )
    return ResultResponse[str](result=f"Successful import {excel.filename}!")


@router.get(
    "/template/download",
    summary="下载测试用例excel模板",
)
async def get_testcase_template():
    """下载测试用例excel模板"""
    template: Path = config.STATIC_PATH / "testcase" / "测试用例模板.xlsx"
    if not template.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="template is not exise!"
        )
    return FileResponse(template, filename="测试用例模板.xlsx")


# @router.get("/getAll")
