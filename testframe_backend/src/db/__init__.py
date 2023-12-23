from passlib.hash import md5_crypt
from tortoise.transactions import in_transaction
from .models import Users, Role, Routes, RouteMeta
from ..utils.log_util import log


async def create_initial_users():
    """创建默认用户/角色"""
    # 查询数据库是否已经有数据
    has_data = await Users.all().exists()
    if not has_data:
        log.info("初始化用户成功，超级管理员：superadmin,12346".center(100, "-"))
        # 创建角色
        super_role = await Role.create(name="superadmin", description="超级管理员角色")
        admin_role = await Role.create(name="admin", description="管理员角色")
        member_role = await Role.create(name="member", description="普通用户角色")
        # 创建默认用户，并添加角色
        super_user = await Users.create(
            username="superadmin",
            descriptions="超级管理员",
            password=md5_crypt.hash("123456"),
            is_super=1,
        )
        admin_user = await Users.create(
            username="admin",
            descriptions="管理员",
            password=md5_crypt.hash("123456"),
        )
        member_user = await Users.create(
            username="user",
            descriptions="普通用户",
            password=md5_crypt.hash("123456"),
        )
        # m2m_manager方式添加manytomany联系
        await super_user.roles.add(super_role)
        await admin_user.roles.add(admin_role)
        await member_user.roles.add(member_role)


async def initial_routes():
    """创建默认路由"""
    # 查询数据库是否已经有数据
    has_data = await Routes.all().exists()
    if not has_data:
        async with in_transaction():
            log.info("开始初始化路由".center(100, "-"))

            # 创建一级路由
            system_route = await Routes.create(
                name="System",
                path="/system",
                hidden=False,
                redirect="noRedirect",
                component="Layout",
                always_show=True,
                is_admin_visible=True
            )

            tool_route = await Routes.create(
                name="Tool",
                path="/tool",
                hidden=False,
                redirect="noRedirect",
                component="Layout",
                always_show=True,
            )
            # 创建二级路由
            system_user_route = await Routes.create(
                name="User",
                path="user",
                hidden=False,
                component="system/user/index",
                parent_id=system_route.id,
            )

            tool_build_route = await Routes.create(
                name="Build",
                path="build",
                hidden=False,
                component="tool/build/index",
                parent_id=tool_route.id,
            )
            # 创建路由meta
            system_meta = await RouteMeta.create(
                icon="system",
                no_cache=False,
                title="系统管理",
                route_id=system_route.id,
            )
            tool_meta = await RouteMeta.create(
                icon="tool",
                no_cache=False,
                title="系统工具",
                route_id=tool_route.id,
            )
            # 二级路由meta
            system_user_meta = await RouteMeta.create(
                icon="user",
                no_cache=False,
                title="用户管理",
                route_id=system_user_route.id,
            )
            tool_build_meta = await RouteMeta.create(
                icon="build",
                no_cache=False,
                title="表单构建",
                route_id=tool_build_route.id,
            )
            log.info("初始化路由成功".center(100, "-"))
