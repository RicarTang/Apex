import json
from fastapi import APIRouter, Depends, Request
from ..core.security import (
    create_access_token,
    check_jwt_auth,
)
from passlib.hash import md5_crypt
from tortoise.exceptions import DoesNotExist
from ...src.db.models import Users
from ..schemas import ResultResponse, user_schema
from ..utils.exceptions.user import (
    UserUnavailableException,
    PasswordValidateErrorException,
    UserNotExistException,
    TokenInvalidException,
)
from ..services import UserTokenService

router = APIRouter()
@router.post(
    "/login",
    summary="登录",
    response_model=ResultResponse[user_schema.Login],
)
async def login(
    request: Request,
    user: user_schema.LoginIn,
):
    """用户登陆."""
    # 查询数据库有无此用户
    try:
        query_user = await Users.get(username=user.username)
    except DoesNotExist:
        raise UserNotExistException
    # 验证密码
    if not md5_crypt.verify(secret=user.password, hash=query_user.password):
        raise PasswordValidateErrorException
    # 用户为黑名单
    if not query_user.is_active:
        raise UserUnavailableException
    # 创建jwt
    access_token = create_access_token(data={"sub": query_user.username})
    # 更新用户jwt
    await UserTokenService.add_jwt(
        current_user_id=query_user.id, token=access_token, client_ip=request.client.host
    )
    return ResultResponse[user_schema.Login](
        result=user_schema.Login(
            data=query_user,
            access_token=access_token,
            token_type="bearer",
        )
    )


@router.post(
    "/logout",
    summary="退出登录",
    response_model=ResultResponse[str],
    dependencies=[Depends(check_jwt_auth)],
)
async def logout(request: Request):
    # 修改当前用户数据库token状态为0
    access_type, access_token = request.headers["authorization"].split(" ")
    if not await UserTokenService.update_token_state(token=access_token):
        raise TokenInvalidException
    return ResultResponse[str](result="Successfully logged out!")


@router.get("/getRouters")
async def get_routers():
    return json.loads(
        """{
    "msg": "操作成功",
    "code": 200,
    "data": [
        {
            "name": "System",
            "path": "/system",
            "hidden": false,
            "redirect": "noRedirect",
            "component": "Layout",
            "alwaysShow": true,
            "meta": {
                "title": "系统管理",
                "icon": "system",
                "noCache": false,
                "link": null
            },
            "children": [
                {
                    "name": "User",
                    "path": "user",
                    "hidden": false,
                    "component": "system/user/index",
                    "meta": {
                        "title": "用户管理",
                        "icon": "user",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Role",
                    "path": "role",
                    "hidden": false,
                    "component": "system/role/index",
                    "meta": {
                        "title": "角色管理",
                        "icon": "peoples",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Menu",
                    "path": "menu",
                    "hidden": false,
                    "component": "system/menu/index",
                    "meta": {
                        "title": "菜单管理",
                        "icon": "tree-table",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Dept",
                    "path": "dept",
                    "hidden": false,
                    "component": "system/dept/index",
                    "meta": {
                        "title": "部门管理",
                        "icon": "tree",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Post",
                    "path": "post",
                    "hidden": false,
                    "component": "system/post/index",
                    "meta": {
                        "title": "岗位管理",
                        "icon": "post",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Dict",
                    "path": "dict",
                    "hidden": false,
                    "component": "system/dict/index",
                    "meta": {
                        "title": "字典管理",
                        "icon": "dict",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Config",
                    "path": "config",
                    "hidden": false,
                    "component": "system/config/index",
                    "meta": {
                        "title": "参数设置",
                        "icon": "edit",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Notice",
                    "path": "notice",
                    "hidden": false,
                    "component": "system/notice/index",
                    "meta": {
                        "title": "通知公告",
                        "icon": "message",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Log",
                    "path": "log",
                    "hidden": false,
                    "redirect": "noRedirect",
                    "component": "ParentView",
                    "alwaysShow": true,
                    "meta": {
                        "title": "日志管理",
                        "icon": "log",
                        "noCache": false,
                        "link": null
                    },
                    "children": [
                        {
                            "name": "Operlog",
                            "path": "operlog",
                            "hidden": false,
                            "component": "monitor/operlog/index",
                            "meta": {
                                "title": "操作日志",
                                "icon": "form",
                                "noCache": false,
                                "link": null
                            }
                        },
                        {
                            "name": "Logininfor",
                            "path": "logininfor",
                            "hidden": false,
                            "component": "monitor/logininfor/index",
                            "meta": {
                                "title": "登录日志",
                                "icon": "logininfor",
                                "noCache": false,
                                "link": null
                            }
                        }
                    ]
                }
            ]
        },
        {
            "name": "Monitor",
            "path": "/monitor",
            "hidden": false,
            "redirect": "noRedirect",
            "component": "Layout",
            "alwaysShow": true,
            "meta": {
                "title": "系统监控",
                "icon": "monitor",
                "noCache": false,
                "link": null
            },
            "children": [
                {
                    "name": "Online",
                    "path": "online",
                    "hidden": false,
                    "component": "monitor/online/index",
                    "meta": {
                        "title": "在线用户",
                        "icon": "online",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Job",
                    "path": "job",
                    "hidden": false,
                    "component": "monitor/job/index",
                    "meta": {
                        "title": "定时任务",
                        "icon": "job",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Druid",
                    "path": "druid",
                    "hidden": false,
                    "component": "monitor/druid/index",
                    "meta": {
                        "title": "数据监控",
                        "icon": "druid",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Server",
                    "path": "server",
                    "hidden": false,
                    "component": "monitor/server/index",
                    "meta": {
                        "title": "服务监控",
                        "icon": "server",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Cache",
                    "path": "cache",
                    "hidden": false,
                    "component": "monitor/cache/index",
                    "meta": {
                        "title": "缓存监控",
                        "icon": "redis",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "CacheList",
                    "path": "cacheList",
                    "hidden": false,
                    "component": "monitor/cache/list",
                    "meta": {
                        "title": "缓存列表",
                        "icon": "redis-list",
                        "noCache": false,
                        "link": null
                    }
                }
            ]
        },
        {
            "name": "Tool",
            "path": "/tool",
            "hidden": false,
            "redirect": "noRedirect",
            "component": "Layout",
            "alwaysShow": true,
            "meta": {
                "title": "系统工具",
                "icon": "tool",
                "noCache": false,
                "link": null
            },
            "children": [
                {
                    "name": "Build",
                    "path": "build",
                    "hidden": false,
                    "component": "tool/build/index",
                    "meta": {
                        "title": "表单构建",
                        "icon": "build",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Gen",
                    "path": "gen",
                    "hidden": false,
                    "component": "tool/gen/index",
                    "meta": {
                        "title": "代码生成",
                        "icon": "code",
                        "noCache": false,
                        "link": null
                    }
                },
                {
                    "name": "Swagger",
                    "path": "swagger",
                    "hidden": false,
                    "component": "tool/swagger/index",
                    "meta": {
                        "title": "系统接口",
                        "icon": "swagger",
                        "noCache": false,
                        "link": null
                    }
                }
            ]
        },
        {
            "name": "Http://ruoyi.vip",
            "path": "http://ruoyi.vip",
            "hidden": false,
            "component": "Layout",
            "meta": {
                "title": "若依官网",
                "icon": "guide",
                "noCache": false,
                "link": "http://ruoyi.vip"
            }
        }
    ]
}"""
    )
