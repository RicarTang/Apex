"""用户业务逻辑层"""

from typing import Tuple, List
from datetime import datetime
from passlib.hash import md5_crypt
from fastapi import HTTPException, status
from tortoise.transactions import in_transaction
from tortoise.exceptions import DoesNotExist, MultipleObjectsReturned
from ...db.models import Users
from ...repositories.management.user import UserRepository
from ...repositories.management.role import RoleRepository
from ...utils.log_util import log
from ...utils.exceptions.user import (
    UserNotExistException,
    RoleNotExistException,
)
from ...schemas.management.user import UserIn, UserResetPwdIn, UserUpdateIn


class UserService:
    """用户服务."""

    @classmethod
    async def query_user_list(
        cls,
        username: str,
        user_status: int,
        begin_time: str,
        end_time: str,
        limit: int,
        page: int,
    ) -> Tuple[List[Users], int]:
        """查询用户列表

        Args:
            username (str): _description_
            user_status (int): _description_
            begin_time (str): _description_
            end_time (str): _description_
            limit (int): _description_
            page (int): _description_

        Returns:
            Tuple[List[Users], int]: _description_
        """
        # 筛选条件
        filters = {}
        if username:
            filters["user_name__icontains"] = username
        if user_status is not None:
            filters["status"] = user_status
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
        # 执行查询
        result, total = await UserRepository.fetch_user_list_by_filter_with_roles(
            limit=limit, page=page, **filters
        )
        return result, total

    @staticmethod
    async def query_user_by_username(username: str) -> Users:
        """通过用户名查询用户

        Raises:
            UserNotExistException: _description_

        Returns:
            _type_: _description_
        """
        try:
            query_result = await Users.get(user_name=username).prefetch_related("roles")
        except DoesNotExist as exc:
            raise UserNotExistException from exc
        except MultipleObjectsReturned as exc:
            log.error("查询出多个同样的用户名！")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Duplicate username!",
            ) from exc
        else:
            return query_result

    @staticmethod
    async def query_user_by_id(user_id: int) -> Users:
        """通过id查询用户

        Args:
            id (int): uid

        Raises:
            UserNotExistException: _description_
            HTTPException: _description_

        Returns:
            Users: _description_
        """
        try:
            query_result = await UserRepository.fetch_by_pk_with_roles(pk=user_id)
        except DoesNotExist as exc:
            raise UserNotExistException from exc
        except MultipleObjectsReturned as exc:
            log.error("查询出多个同样的用户名！")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Duplicate username!",
            ) from exc
        else:
            return query_result

    @staticmethod
    async def create_user(body: UserIn) -> Users:
        """创建用户

        Args:
            body (UserIn): 请求body

        Raises:
            RoleNotExistException: _description_

        Returns:
            Users: _description_
        """
        body.password = md5_crypt.hash(body.password)
        async with in_transaction():
            user_obj = await UserRepository.create(
                **body.model_dump(exclude_unset=True)
            )
            # 查询角色列表
            roles = await RoleRepository.fetch_all_by_filter(id__in=body.user_roles)
            if not roles:
                raise RoleNotExistException
            # 添加角色关联
            await user_obj.roles.add(*roles)
        log.info(f"成功创建用户：{body.model_dump(exclude_unset=True)}")
        return await UserService.query_user_by_id(user_obj.id)

    @staticmethod
    async def is_super_user(user_id: int) -> bool:
        """判断是否是超级管理员

        Args:
            user_id (int): 用户id

        Returns:
            bool: _description_
        """
        user = await UserRepository.fetch_by_filter_with_roles(
            pk=user_id, roles__is_super=True
        )
        if user:
            return True
        return False

    @classmethod
    async def update_user_pwd(cls, body: UserResetPwdIn) -> None:
        """更新用户密码

        Args:
            body (UserResetPwdIn): 请求body

        Raises:
            UserNotExistException: _description_

        """
        user_exists = await UserRepository.fetch_by_pk(pk=body.user_id)
        if not user_exists:
            raise UserNotExistException
        updated_num = await UserRepository.update(
            pk=body.user_id, password=md5_crypt.hash(body.password)
        )
        if updated_num:
            log.info(f"成功更新了id:{body.user_id}密码")
        else:
            log.error(f"因为用户不存在更新id:{body.user_id}的密码失败")
            raise UserNotExistException

    @classmethod
    async def delete_user_from_id(cls, user_list: list) -> None:
        """删除用户

        Args:
            user_list (list): 用户id列表

        Raises:
            HTTPException: _description_
            UserNotExistException: _description_
        """

        # 检查是否存在admin用户
        has_admin = await UserRepository.exists(id__in=user_list, user_name="admin")
        # 禁止删除admin用户
        if has_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="admin is prohibited from being deleted",
            )

        delete_count = await UserRepository.delete_by_filter(
            id__in=user_list, user_name__not="admin"
        )
        if not delete_count:
            raise UserNotExistException

    @classmethod
    async def update_user_from_id(cls, user_id: int, body: UserUpdateIn) -> None:
        """更新用户

        Args:
            user_id (int): user id
            body (UserUpdateIn): 请求body

        Raises:
            UserNotExistException: _description_
            HTTPException: _description_
        """
        # 查询用户是否存在
        query_user = await UserRepository.fetch_by_pk_with_roles(pk=user_id)
        if not query_user:
            raise UserNotExistException
        # 启用事务
        async with in_transaction():
            # 判断角色修改
            if body.user_roles is not None:
                if body.user_roles == []:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Role cannot be cleared!",
                    )
                # 获取当前用户角色列表
                current_user_role_list = await query_user.roles.all()
                # 获取接口请求角色列表
                roles = await RoleRepository.fetch_all_by_filter(id__in=body.user_roles)
                # 确定需要添加和需要移除的角色 ID
                role_ids_to_add = list(set(roles) - set(current_user_role_list))
                role_ids_to_remove = list(set(current_user_role_list) - set(roles))
                log.debug(f"toadd:{role_ids_to_add},toremove:{role_ids_to_remove}")
                # 添加/删除
                await query_user.roles.add(*role_ids_to_add)
                if role_ids_to_remove:
                    await query_user.roles.remove(*role_ids_to_remove)
            # 更新指定字段
            await UserRepository.update(
                pk=user_id,
                **body.model_dump(exclude_unset=True, exclude=["user_roles"]),
            )
