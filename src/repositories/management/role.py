"""角色数据访问模块"""

from ...repositories import BaseRepository
from ...db.models import Role


class RoleRepository(BaseRepository[Role]):
    """角色数据访问仓库

    Args:
        BaseRepository (_type_): _description_
    """

    model = Role
