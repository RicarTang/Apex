# from ..db.models import Users


# class PermissionAccess:
#     """权限服务"""

#     @staticmethod
#     async def has_access(user_id: int, model: str, action: str) -> bool:
#         """判断用户是否有访问权限"""
#         # 获取用户角色权限访问控制
#         user = await Users.filter(
#                 id=user_id,
#                 roles__permissions__model=model,
#                 roles__permissions__action=action,
#             ).first().prefetch_related("roles__permissions")
#         if user:
#             return True
#         else:
#             return False

#     # @staticmethod
#     # async def get_menus(user_id: int):
#     #     user = await Users.filter(
#     #         id=user_id
#     #     ).first().prefetch_related("roles__menus")