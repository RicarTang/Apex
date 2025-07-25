from datetime import datetime
from pathlib import Path
from typing import Optional, Any
from fastapi import (
    APIRouter,
    HTTPException,
    UploadFile,
    Query,
    status,
)
from typing_extensions import Annotated
from pydantic import StringConstraints
from fastapi.responses import FileResponse
from tortoise.exceptions import DoesNotExist

from src.schemas.autotest import testcase
from src.config import config
from src.core.redis import RedisService
from src.services import TestCaseService
from src.db.models import TestCase
from src.schemas import ResultResponse
from src.utils.log_util import log
from src.utils.excel_util import save_file, read_all_testcase
from src.utils.exceptions.testcase import TestcaseNotExistException
from src.utils.exceptions.testenv import CurrentTestEnvNotSetException

router = APIRouter()


@router.post(
    "/add",
    summary="添加测试用例",
    response_model=ResultResponse[testcase.TestCaseOut],
)
async def add_testcase(body: testcase.TestCaseIn):
    """添加测试用例"""
    result = await TestCaseService.add_testcase(body.model_dump(exclude_unset=True))
    return ResultResponse[testcase.TestCaseOut](result=result)


@router.post(
    "/import",
    summary="导入excel测试用例",
    response_model=ResultResponse[None],
)
async def add_testcases(file: UploadFile):
    """导入测试用例"""
    if file.filename.endswith(("xlsx", "csv", "xls")):
        # 保存文件名
        save_name = str(datetime.now().strftime("%Y-%m-%d-%H-%M-%S")) + file.filename
        # 保存路径
        save_path = config.STATIC_PATH / "testcase" / "upload" / save_name
        # 保存上传的文件
        await save_file(
            file=file,
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
    return ResultResponse[None](message=f"Successful import {file.filename}!")


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
    "/list",
    summary="获取测试用例列表",
    response_model=ResultResponse[testcase.TestCaseListOut],
)
async def get_all_testcase(
    case_title: Optional[str] = Query(
        default=None, alias="caseTitle", description="用例筛选"
    ),
    case_suite: Optional[str] = Query(
        default=None, alias="caseSuite", description="用例所属套件筛选"
    ),
    case_module: Optional[str] = Query(
        default=None, alias="caseModule", description="用例所属套件筛选"
    ),
    begin_time: Optional[str] = Query(
        default=None, description="开始时间", alias="beginTime"
    ),
    end_time: Optional[str] = Query(default=None, description="结束时间", alias="endTime"),
    limit: Optional[int] = Query(default=20, ge=10),
    page: Optional[int] = Query(default=1, gt=0),
):
    """获取测试用例列表"""
    filters = {}
    if case_title:
        filters["case_title__icontains"] = case_title
    if case_suite:
        filters["testsuites__suite_title__icontains"] = case_suite
    if case_module:
        filters["case_module__icontains"] = case_module
    if begin_time:
        begin_time = datetime.strptime(begin_time, "%Y-%m-%d")
        filters["created_at__gte"] = begin_time
    if end_time:
        end_time = datetime.strptime(end_time, "%Y-%m-%d")
        filters["created_at__lte"] = end_time
    if begin_time and end_time:
        filters["created_at__range"] = (
            begin_time,
            end_time,
        )
    query = TestCase.filter(**filters)
    testcases = await query.offset(limit * (page - 1)).limit(limit).all()
    total = await query.count()
    return ResultResponse[testcase.TestCaseListOut](
        result=testcase.TestCaseListOut(
            data=testcases,
            page=page,
            limit=limit,
            total=total,
        )
    )


@router.post(
    "/executeOne",
    summary="执行单条测试用例",
    response_model=ResultResponse[testcase.ExecuteTestcaseOut],
)
async def execute_testcase(
    body: testcase.ExecuteTestcaseIn,
):
    """执行测试用例"""
    case = await TestCase.filter(id=body.case_id).first()
    current_env = await RedisService().aioredis_pool.get("test:currentEnv")
    if not current_env:
        raise CurrentTestEnvNotSetException
    if not case:
        raise TestcaseNotExistException
    # 执行用例逻辑
    result = await TestCaseService.execute_testcase(
        testcase=case, current_env=current_env
    )
    res_time = result.elapsed.total_seconds() * 1000
    log.debug(res_time)
    res = dict(
        code=result.status_code,
        time=res_time,
        headers=dict(result.headers),
        body=result.json(),
    )
    return ResultResponse[testcase.ExecuteTestcaseOut](result=res)


@router.delete(
    "/{case_ids}",
    summary="删除测试用例",
    response_model=ResultResponse[None],
)
async def delete_testcase(case_ids: Annotated[str, StringConstraints(strip_whitespace=True, pattern=r'^\d+(,\d+)*$')]):
    """删除测试用例"""
    source_ids_list = case_ids.split(",")
    delete_count = await TestCase.filter(id__in=source_ids_list).delete()
    if not delete_count:
        raise TestcaseNotExistException
    return ResultResponse[None](message="successful deleted testcase!")


@router.get(
    "/{case_id}",
    summary="获取指定testcase",
    response_model=ResultResponse[testcase.TestCaseOut],
)
async def get_testcase(case_id: int):
    """获取指定testcase"""
    try:
        case = await TestCase.get(id=case_id)
    except DoesNotExist:
        raise TestcaseNotExistException
    return ResultResponse[testcase.TestCaseOut](result=case)


@router.put(
    "/{case_id}",
    summary="更新测试用例",
    response_model=ResultResponse[None],
)
async def update_testcase(case_id: int, body: testcase.UpdateCaseIn):
    """更新测试用例数据"""
    update_count = await TestCase.filter(id=case_id).update(
        **body.model_dump(exclude_unset=True)
    )
    if not update_count:
        raise TestcaseNotExistException
    return ResultResponse[None](message="successful updated testcase!")
