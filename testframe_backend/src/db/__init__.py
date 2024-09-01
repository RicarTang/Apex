from asyncio import current_task
from typing import Tuple
from passlib.hash import md5_crypt
# from .models import Users, Role, Routes, RouteMeta, Permission
from .enum import AccessModelEnum, AccessActionEnum, BoolEnum, DisabledEnum
from ..utils.log_util import log
from ...config import config

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
    async_scoped_session,
)


# def create_database():
#     """
#     当db不存在时，自动创建db
#     """
#     engine = create_engine(config.SYNC_SQLALCHEMY_URL, echo=True)
#     with engine.connect() as conn:
#         conn.execute(
#             "CREATE DATABASE IF NOT EXISTS apex default character set utf8mb4 collate utf8mb4_unicode_ci"
#         )
#     # close engine
#     engine.dispose()


# # 优先建库
# create_database()
# 同步引擎
engine = create_engine(config.ASYNC_SQLALCHEMY_URL, pool_recycle=1500)
# 异步engine
async_engine = create_async_engine(
    config.ASYNC_SQLALCHEMY_URL, max_overflow=0, pool_size=50, pool_recycle=1500
)


async_session = async_scoped_session(
    async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False),
    scopefunc=current_task,
)


# class InitDbData:
#     """初始化数据库数据"""

#     async def execute_init(self):
#         """执行"""
#         if not await self.db_has_data():
#             async with in_transaction():
#                 # 初始化用户
#                 admin_user, member_user = await self.init_user()
#                 # 插入用户
#                 await admin_user.save()
#                 await member_user.save()
#                 # 初始化角色
#                 admin_role, member_role = await self.init_role()
#                 # 插入角色
#                 await admin_role.save()
#                 await member_role.save()
#                 # 添加用户角色关联
#                 await admin_user.roles.add(admin_role)
#                 await member_user.roles.add(member_role)
#                 # 初始化权限
#                 (
#                     apitest_add_access,
#                     apitest_del_access,
#                     apitest_update_access,
#                     apitest_query_access,
#                 ) = await self.init_permission()
#                 # 插入权限控制
#                 await apitest_add_access.save()
#                 await apitest_del_access.save()
#                 await apitest_update_access.save()
#                 await apitest_query_access.save()
#                 # 添加member角色权限关联
#                 await member_role.permissions.add(
#                     apitest_add_access,
#                     apitest_del_access,
#                     apitest_update_access,
#                     apitest_query_access,
#                 )
#                 # 初始化菜单路由
#                 (
#                     system_route,
#                     test_route,
#                     system_user_route,
#                     test_case_route,
#                     system_role_route,
#                     system_menu_route,
#                     test_suite_route,
#                     test_env_route,
#                     system_permission_route,
#                 ) = await self.init_menu_route()

#                 # 初始化菜单路由meta
#                 (
#                     system_meta,
#                     test_meta,
#                     system_user_meta,
#                     test_case_meta,
#                     system_role_meta,
#                     system_menu_meta,
#                     test_suite_meta,
#                     test_env_meta,
#                     system_permission_meta,
#                 ) = await self.init_menu_meta()

#                 await system_meta.save()
#                 await test_meta.save()
#                 await system_user_meta.save()
#                 await test_case_meta.save()
#                 await system_role_meta.save()
#                 await system_menu_meta.save()
#                 await test_suite_meta.save()
#                 await test_env_meta.save()
#                 await system_permission_meta.save()
#                 # 添加外键
#                 # 插入菜单路由
#                 system_route.route_meta = system_meta
#                 test_route.route_meta = test_meta
#                 await system_route.save()
#                 await test_route.save()

#                 system_user_route.parent_id = system_route.id
#                 test_case_route.parent_id = test_route.id
#                 system_role_route.parent_id = system_route.id
#                 system_menu_route.parent_id = system_route.id
#                 test_suite_route.parent_id = test_route.id
#                 test_env_route.parent_id = test_route.id
#                 system_permission_route.parent_id = system_route.id
#                 # 添加meta
#                 system_user_route.route_meta = system_user_meta
#                 test_case_route.route_meta = test_case_meta
#                 system_role_route.route_meta = system_role_meta
#                 system_menu_route.route_meta = system_menu_meta
#                 test_suite_route.route_meta = test_suite_meta
#                 test_env_route.route_meta = test_env_meta
#                 system_permission_route.route_meta = system_permission_meta
#                 await system_user_route.save()
#                 await test_case_route.save()
#                 await system_role_route.save()
#                 await system_menu_route.save()
#                 await test_suite_route.save()
#                 await test_env_route.save()
#                 await system_permission_route.save()

#                 # 菜单角色关联
#                 await member_role.menus.add(
#                     test_route, test_case_route, test_suite_route, test_env_route
#                 )
#                 log.info("初始化完成!".center(100, "-"))

#     async def db_has_data(self) -> bool:
#         """查询数据库是否已经有数据"""
#         return await Users.all().exists()

#     async def init_user(self) -> Tuple[Users]:
#         """初始化用户"""
#         log.info("开始初始化用户,管理员: admin,12346".center(100, "-"))
#         # 创建默认用户
#         admin_user = Users(
#             user_name="admin",
#             remark="管理员",
#             password=md5_crypt.hash("123456"),
#         )
#         member_user = Users(
#             user_name="tester",
#             remark="普通用户",
#             password=md5_crypt.hash("123456"),
#         )
#         return admin_user, member_user

#     async def init_role(self) -> Tuple[Role]:
#         """初始化角色"""
#         log.info("开始初始化角色".center(100, "-"))
#         # 创建默认角色
#         admin_role = Role(
#             role_name="管理员", role_key="admin", remark="管理员角色", is_super=True
#         )
#         member_role = Role(
#             role_name="普通用户", role_key="member", remark="普通用户角色", is_super=False
#         )
#         return admin_role, member_role

#     async def init_permission(self) -> Tuple[Permission]:
#         """初始化权限"""
#         log.info("开始初始化权限".center(100, "-"))
#         apitest_add_access = Permission(
#             name="test模块添加权限",
#             model=AccessModelEnum.APITEST,
#             action=AccessActionEnum.ADD,
#         )
#         apitest_del_access = Permission(
#             name="test模块删除权限",
#             model=AccessModelEnum.APITEST,
#             action=AccessActionEnum.DEL,
#         )
#         apitest_update_access = Permission(
#             name="test模块更新权限",
#             model=AccessModelEnum.APITEST,
#             action=AccessActionEnum.PUT,
#         )
#         apitest_query_access = Permission(
#             name="test模块查询权限",
#             model=AccessModelEnum.APITEST,
#             action=AccessActionEnum.GET,
#         )
#         return (
#             apitest_add_access,
#             apitest_del_access,
#             apitest_update_access,
#             apitest_query_access,
#         )

#     async def init_menu_route(self) -> Tuple[Routes]:
#         """初始化路由菜单"""
#         log.info("开始初始化菜单路由".center(100, "-"))
#         # 创建系统管理菜单路由
#         # 系统管理菜单
#         system_route = Routes(
#             name="System",
#             path="/system",
#             hidden=False,
#             redirect="noRedirect",
#             component="Layout",
#             always_show=True,
#         )
#         # 系统管理菜单子菜单用户管理
#         system_user_route = Routes(
#             name="User",
#             path="user",
#             hidden=False,
#             component="system/user/index",
#         )
#         # 系统管理菜单子菜单角色管理
#         system_role_route = Routes(
#             name="Role",
#             path="role",
#             hidden=False,
#             component="system/role/index",
#         )
#         # 系统管理菜单子菜单菜单管理
#         system_menu_route = Routes(
#             name="Menu",
#             path="menu",
#             hidden=False,
#             component="system/menu/index",
#         )
#         # 系统管理菜单子菜单权限管理
#         system_permission_route = Routes(
#             name="Permission",
#             path="permission",
#             hidden=False,
#             component="system/permission/index",
#         )
#         # 创建apiTest菜单路由
#         # 测试菜单
#         test_route = Routes(
#             name="Test",
#             path="/test",
#             hidden=False,
#             redirect="noRedirect",
#             component="Layout",
#             always_show=True,
#         )
#         # 测试子菜单用例管理
#         test_case_route = Routes(
#             name="Case",
#             path="case",
#             hidden=False,
#             component="test/case/index",
#         )
#         # 测试子菜单套件管理
#         test_suite_route = Routes(
#             name="Suite",
#             path="suite",
#             hidden=False,
#             component="test/suite/index",
#         )
#         # 测试子菜单环境管理
#         test_env_route = Routes(
#             name="Env",
#             path="env",
#             hidden=False,
#             component="test/env/index",
#         )
#         return (
#             system_route,
#             test_route,
#             system_user_route,
#             test_case_route,
#             system_role_route,
#             system_menu_route,
#             test_suite_route,
#             test_env_route,
#             system_permission_route,
#         )

#     async def init_menu_meta(self) -> Tuple[RouteMeta]:
#         """初始化菜单路由meta"""
#         log.info("开始初始化菜单路由meta".center(100, "-"))
#         # 系统管理meta
#         system_meta = RouteMeta(
#             icon="system",
#             no_cache=False,
#             title="系统管理",
#         )
#         system_user_meta = RouteMeta(
#             icon="user",
#             no_cache=False,
#             title="用户管理",
#         )
#         system_role_meta = RouteMeta(
#             icon="peoples",
#             no_cache=False,
#             title="角色管理",
#         )
#         system_menu_meta = RouteMeta(
#             icon="tree-table",
#             no_cache=False,
#             title="菜单管理",
#         )
#         system_permission_meta = RouteMeta(
#             icon="lock",
#             no_cache=False,
#             title="权限管理",
#         )
#         # 接口测试meta
#         test_meta = RouteMeta(
#             icon="swagger",
#             no_cache=False,
#             title="接口测试",
#         )
#         test_case_meta = RouteMeta(
#             icon="excel",
#             no_cache=False,
#             title="用例管理",
#         )
#         test_suite_meta = RouteMeta(
#             icon="tab",
#             no_cache=False,
#             title="套件管理",
#         )
#         test_env_meta = RouteMeta(
#             icon="time-range",
#             no_cache=False,
#             title="测试环境管理",
#         )
#         return (
#             system_meta,
#             test_meta,
#             system_user_meta,
#             test_case_meta,
#             system_role_meta,
#             system_menu_meta,
#             test_suite_meta,
#             test_env_meta,
#             system_permission_meta,
#         )
