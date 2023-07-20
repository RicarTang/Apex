from passlib.hash import md5_crypt
from .models import Users, Role
from ..utils.log_util import log


async def create_initial_users():
    """创建默认用户/角色"""
    # 查询数据库是否已经有数据
    has_data = await Users.all().exists()
    if not has_data:
        log.info("初始化用户成功，超级管理员：superadmin,12346".center("-",100))
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
