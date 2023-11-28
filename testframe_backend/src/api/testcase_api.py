# import time
from datetime import datetime
from pathlib import Path
from typing import Optional, List
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
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectionError
from aioredis import Redis
from ...config import config
from ..core.cache import aioredis_pool
from ..services import TestCaseService
from ..db.models import TestCase
from ..schemas import ResultResponse, testcase_schema
from ..utils.log_util import log
from ..utils.excel_util import save_file, read_all_testcase
from ..utils.exceptions.testcase import TestcaseNotExistException

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
    result = await TestCaseService.add_testcase(body.dict())
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
        await TestCaseService.add_testcase_from_list(testcase_list)
    else:
        # 上传文件格式错误
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="template suffix is error!"
        )
    return ResultResponse[str](message=f"Successful import {excel.filename}!")


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


@router.get(
    "/getAll",
    summary="获取所有测试用例",
    response_model=ResultResponse[testcase_schema.TestCasesTo],
)
async def get_all_testcase(
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取所有测试用例

    Args:
        limit (Optional[int], optional): _description_. Defaults to Query(default=20, ge=10).
        page (Optional[int], optional): _description_. Defaults to Query(default=1, gt=0).
    """
    testcases = await TestCase.all().offset(limit * (page - 1)).limit(limit)
    total = await TestCase.all().count()
    return ResultResponse[testcase_schema.TestCasesTo](
        result=testcase_schema.TestCasesTo(
            data=testcases,
            page=page,
            limit=limit,
            total=total,
        )
    )


@router.get(
    "/query",
    summary="查询测试用例",
    response_model=ResultResponse[testcase_schema.TestCasesTo],
    # dependencies=[Depends(check_jwt_auth)],
)
async def query_testcase(
    case_title: Optional[str] = Query(default=None, description="用例标题"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """查询测试用例"""
    result = await TestCase.filter(case_title__contains=case_title).all()
    total = len(result)
    return ResultResponse[testcase_schema.TestCasesTo](
        result=testcase_schema.TestCasesTo(
            data=result, page=page, limit=limit, total=total
        )
    )


@router.get(
    "/{case_id}",
    summary="获取指定testcase",
    response_model=ResultResponse[testcase_schema.TestCaseTo],
)
async def get_testcase(case_id: int):
    """获取指定testcase

    Args:
        case_id (int): _description_. Defaults to Query(gt=0).
    """
    try:
        testcase = await TestCase.get(id=case_id)
    except DoesNotExist:
        raise TestcaseNotExistException
    return ResultResponse[testcase_schema.TestCaseTo](result=testcase)


@router.put(
    "/{case_id}",
    summary="更新测试用例",
    response_model=ResultResponse[testcase_schema.TestCaseTo],
)
async def update_testcase(case_id: int, body: dict):
    """更新测试用例数据

    Args:
        body (dict): _description_
    """
    if not await TestCase.filter(id=case_id).exists():
        raise TestcaseNotExistException
    result = await TestCase.filter(id=case_id).update(**body.dict(exclude_unset=True))
    log.debug(f"update更新{result}条数据")
    return ResultResponse[testcase_schema.TestCaseTo](
        result=await TestCase.get(id=case_id)
    )


@router.delete(
    "/{case_id}",
    summary="删除测试用例",
    response_model=ResultResponse[str],
)
async def delete_testcase(case_id: int):
    """删除指定id的测试用例

    Args:
        case_id (int): _description_
    """
    if not await TestCase.filter(id=case_id).exists():
        raise TestcaseNotExistException
    result = await TestCase.filter(id=case_id).delete()
    return ResultResponse[str](message="successful deleted testcase!")


@router.post(
    "/executeOne",
    summary="执行单条测试用例",
)
async def execute_testcase(
    body: testcase_schema.ExecuteTestcaseIn, redis: Redis = Depends(aioredis_pool)
):
    """执行测试用例

    Args:
        body (testcase_schema.ExecuteTestcaseIn): 前端给case_id
        redis (Redis, optional): _description_. Defaults to Depends(aioredis_pool).

    Returns:
        _type_: _description_
    """
    testcase = await TestCase.filter(id=body.case_id).first()
    current_env = await redis.get("currentEnv")
    if not testcase:
        raise TestcaseNotExistException
    async with ClientSession() as session:
        try:
            async with session.request(
                testcase.api_method, current_env.decode('utf-8') + testcase.api_path
            ) as resp:
                res = await resp.json()
        except ClientConnectionError as e:
            raise HTTPException(status_code=200,detail=e)
        else:
            return res


@router.post(
    "/executeAll",
    summary="执行所有测试用例",
)
async def execute_all_testcase():
    """待完善"""
    return
