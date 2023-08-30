from fastapi import APIRouter
from ..db.models import TestEnv
from ..schemas import ResultResponse, testenv_schema
from ..utils.log_util import log


router = APIRouter()


@router.post(
    "/add",
    summary="添加测试环境地址",
    response_model=ResultResponse[testenv_schema.TestEnvTo],
)
async def add_test_env_ip(body: testenv_schema.TestEnvIn):
    """添加测试环境地址

    Args:
        body (testenv_schema.TestEnvIn): _description_
    """
    result = await TestEnv.create(**body.dict())
    return ResultResponse[testenv_schema.TestEnvTo](result=result)
