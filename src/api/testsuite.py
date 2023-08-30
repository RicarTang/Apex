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
from ..schemas import ResultResponse, testsuite_schema
from ..utils.log_util import log


router = APIRouter()


@router.post(
    "/add",
    summary="添加测试套件",

)
async def add_testsuite(body:testsuite_schema.TestSuiteIn):
    pass

@router.get(
    "/getAll",
    summary="获取所有测试套件",

)
async def get_all_testsuite(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取所有测试套件

    Args:
        limit (Optional[int], optional): _description_. Defaults to Query(default=20, ge=10).
        page (Optional[int], optional): _description_. Defaults to Query(default=1, gt=0).
    """
    pass


@router.get(
    "/{suite_id}",
    summary="获取指定testsuite",
    response_model=ResultResponse[testsuite_schema.TestSuiteTo],
)
async def get_testsuite():
    pass