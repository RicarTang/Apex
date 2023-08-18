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
from src.db.models import Users, Role
from ..schemas import schemas
from ..utils.log_util import log
from config import config

router = APIRouter()


@router.post(
    "/import",
    summary="导入测试用例",
    response_model=schemas.ResultResponse[str],
)
async def add_testcases(excel: UploadFile):
    """导入测试用例

    Args:
        excel (UploadFile): excel测试用例

    Returns:
        _type_: _description_
    """
    if excel.filename.endswith(("xlsx", "csv", "xls")):
        log.debug("格式正确")
    else:
        log.debug("格式错误")

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
