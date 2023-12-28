import asyncio
from typing import Tuple
from passlib.hash import md5_crypt
from tortoise.transactions import in_transaction
from .models import Users, Role, Routes, RouteMeta, Permission, AccessControl, DataDict
from .enum import AccessModelEnum, AccessActionEnum, BoolEnum, DisabledEnum
from ..utils.log_util import log


class InitDbData:
    """初始化数据库数据"""

    async def execute_init(self):
        """执行"""
        if not await self.db_has_data():
            async with in_transaction():
                # 初始化用户
                admin_user, member_user = await self.init_user()
                # 插入用户
                await admin_user.save()
                await member_user.save()
                # 初始化角色
                admin_role, member_role = await self.init_role()
                # 插入角色
                await admin_role.save()
                await member_role.save()
                # 添加用户角色关联
                await admin_user.roles.add(admin_role)
                await member_user.roles.add(member_role)
                # 初始化权限
                admin_permission, member_permission = await self.init_permission()
                # 插入权限
                await admin_permission.save()
                await member_permission.save()
                # 添加角色权限关联
                await admin_role.permissions.add(admin_permission)
                await member_role.permissions.add(member_permission)
                # 初始化访问控制
                (
                    apitest_add_access,
                    apitest_del_access,
                    apitest_update_access,
                    apitest_query_access,
                ) = await self.init_access()
                # 插入访问控制
                await apitest_add_access.save()
                await apitest_del_access.save()
                await apitest_update_access.save()
                await apitest_query_access.save()
                # 添加member权限访问控制关联
                await member_permission.accesses.add(
                    apitest_add_access,
                    apitest_del_access,
                    apitest_update_access,
                    apitest_query_access,
                )
                # 初始化菜单路由
                (
                    system_route,
                    test_route,
                    system_user_route,
                    test_case_route,
                    system_dict_route,
                    system_role_route,
                    system_menu_route,
                    test_suite_route,
                    test_env_route,
                ) = await self.init_menu_route()
                # 插入菜单路由
                await system_route.save()
                await test_route.save()
                # 添加外键
                system_user_route.parent_id = system_route.id
                test_case_route.parent_id = test_route.id
                system_dict_route.parent_id = system_route.id
                system_role_route.parent_id = system_route.id
                system_menu_route.parent_id = system_route.id
                test_suite_route.parent_id = test_route.id
                test_env_route.parent_id = test_route.id
                await system_user_route.save()
                await test_case_route.save()
                await system_dict_route.save()
                await system_role_route.save()
                await system_menu_route.save()
                await test_suite_route.save()
                await test_env_route.save()
                # 初始化菜单路由meta
                (
                    system_meta,
                    test_meta,
                    system_user_meta,
                    test_case_meta,
                    system_dict_meta,
                    system_role_meta,
                    system_menu_meta,
                    test_suite_meta,
                    test_env_meta,
                ) = await self.init_menu_meta()
                # 插入菜单路由meita
                system_meta.route = system_route
                test_meta.route = test_route
                system_user_meta.route = system_user_route
                test_case_meta.route = test_case_route
                system_dict_meta.route = system_dict_route
                system_role_meta.route = system_role_route
                system_menu_meta.route = system_menu_route
                test_suite_meta.route = test_suite_route
                test_env_meta.route = test_env_route
                await system_meta.save()
                await test_meta.save()
                await system_user_meta.save()
                await test_case_meta.save()
                await system_dict_meta.save()
                await system_role_meta.save()
                await system_menu_meta.save()
                await test_suite_meta.save()
                await test_env_meta.save()
                # 菜单权限关联
                await member_permission.menus.add(test_route)
                # 初始化数据字典
                await self.init_data_dict()
                log.info("初始化完成!".center(100, "-"))

    async def db_has_data(self) -> bool:
        """查询数据库是否已经有数据"""
        return await Users.all().exists()

    async def init_user(self) -> Tuple[Users]:
        """初始化用户"""
        log.info("开始初始化用户,管理员: admin,12346".center(100, "-"))
        # 创建默认用户
        admin_user = Users(
            username="admin",
            descriptions="管理员",
            password=md5_crypt.hash("123456"),
        )
        member_user = Users(
            username="tester",
            descriptions="普通用户",
            password=md5_crypt.hash("123456"),
        )
        return admin_user, member_user

    async def init_role(self) -> Tuple[Role]:
        """初始化角色"""
        log.info("开始初始化角色".center(100, "-"))
        # 创建默认角色
        admin_role = Role(name="admin", description="管理员角色", is_super=True)
        member_role = Role(name="member", description="普通用户角色", is_super=False)
        return admin_role, member_role

    async def init_permission(self) -> Tuple[Permission]:
        """初始化权限"""
        log.info("开始初始化权限".center(100, "-"))
        admin_permission = Permission(name="admin权限")
        member_permission = Permission(name="member权限")
        return admin_permission, member_permission

    async def init_access(self) -> Tuple[AccessControl]:
        """初始化访问控制"""
        log.info("开始初始化访问控制".center(100, "-"))
        apitest_add_access = AccessControl(
            name="test模块添加权限",
            model=AccessModelEnum.APITEST,
            action=AccessActionEnum.ADD,
        )
        apitest_del_access = AccessControl(
            name="test模块删除权限",
            model=AccessModelEnum.APITEST,
            action=AccessActionEnum.DEL,
        )
        apitest_update_access = AccessControl(
            name="test模块更新权限",
            model=AccessModelEnum.APITEST,
            action=AccessActionEnum.PUT,
        )
        apitest_query_access = AccessControl(
            name="test模块查询权限",
            model=AccessModelEnum.APITEST,
            action=AccessActionEnum.GET,
        )
        return (
            apitest_add_access,
            apitest_del_access,
            apitest_update_access,
            apitest_query_access,
        )

    async def init_menu_route(self) -> Tuple[Routes]:
        """初始化路由菜单"""
        log.info("开始初始化菜单路由".center(100, "-"))
        # 创建系统管理菜单路由
        # 系统管理菜单
        system_route = Routes(
            name="System",
            path="/system",
            hidden=False,
            redirect="noRedirect",
            component="Layout",
            always_show=True,
        )
        # 系统管理菜单子菜单用户管理
        system_user_route = Routes(
            name="User",
            path="user",
            hidden=False,
            component="system/user/index",
        )
        # 系统管理菜单子菜单字典管理
        system_dict_route = Routes(
            name="Dict",
            path="dict",
            hidden=False,
            component="system/dict/index",
        )
        # 系统管理菜单子菜单角色管理
        system_role_route = Routes(
            name="Role",
            path="role",
            hidden=False,
            component="system/role/index",
        )
        # 系统管理菜单子菜单菜单管理
        system_menu_route = Routes(
            name="Menu",
            path="menu",
            hidden=False,
            component="system/menu/index",
        )
        # 创建apiTest菜单路由
        # 测试菜单
        test_route = Routes(
            name="Test",
            path="/test",
            hidden=False,
            redirect="noRedirect",
            component="Layout",
            always_show=True,
        )
        # 测试子菜单用例管理
        test_case_route = Routes(
            name="Case",
            path="case",
            hidden=False,
            component="test/case/index",
        )
        # 测试子菜单套件管理
        test_suite_route = Routes(
            name="Suite",
            path="suite",
            hidden=False,
            component="test/suite/index",
        )
        # 测试子菜单环境管理
        test_env_route = Routes(
            name="Env",
            path="env",
            hidden=False,
            component="test/env/index",
        )
        return (
            system_route,
            test_route,
            system_user_route,
            test_case_route,
            system_dict_route,
            system_role_route,
            system_menu_route,
            test_suite_route,
            test_env_route,
        )

    async def init_menu_meta(self) -> Tuple[RouteMeta]:
        """初始化菜单路由meta"""
        log.info("开始初始化菜单路由meta".center(100, "-"))
        # 系统管理meta
        system_meta = RouteMeta(
            icon="system",
            no_cache=False,
            title="系统管理",
        )
        system_user_meta = RouteMeta(
            icon="user",
            no_cache=False,
            title="用户管理",
        )
        system_dict_meta = RouteMeta(
            icon="dict",
            no_cache=False,
            title="字典管理",
        )
        system_role_meta = RouteMeta(
            icon="peoples",
            no_cache=False,
            title="角色管理",
        )
        system_menu_meta = RouteMeta(
            icon="tree-table",
            no_cache=False,
            title="菜单管理",
        )
        # 接口测试meta
        test_meta = RouteMeta(
            icon="swagger",
            no_cache=False,
            title="接口测试",
        )
        test_case_meta = RouteMeta(
            icon="build",
            no_cache=False,
            title="用例管理",
        )
        test_suite_meta = RouteMeta(
            icon="build",
            no_cache=False,
            title="套件管理",
        )
        test_env_meta = RouteMeta(
            icon="build",
            no_cache=False,
            title="测试环境管理",
        )
        return (
            system_meta,
            test_meta,
            system_user_meta,
            test_case_meta,
            system_dict_meta,
            system_role_meta,
            system_menu_meta,
            test_suite_meta,
            test_env_meta,
        )

    async def init_data_dict(self) -> None:
        """初始化字典数据"""
        await DataDict.bulk_create(
            [
                DataDict(
                    dict_type="sys_normal_disable",
                    dict_label="正常",
                    dict_value="1",
                    is_default=BoolEnum.TRUE,
                    remark="正常状态",
                ),
                DataDict(
                    dict_type="sys_normal_disable",
                    dict_label="停用",
                    dict_value="0",
                    is_default=BoolEnum.FALSE,
                    remark="停用状态",
                ),
            ]
        )
