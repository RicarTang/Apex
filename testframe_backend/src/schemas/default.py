from typing import List
from ..db.models import RouteMetaPydantic, RoutesPydantic


class Routes(RoutesPydantic):
    meta: RouteMetaPydantic


class RoutesTo(Routes):
    """routes res"""

    children: List[Routes]
