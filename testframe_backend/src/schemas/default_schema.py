from typing import List, Optional
from pydantic import BaseModel, Field, Extra
from ..db.models import RouteMetaPydantic, RoutesPydantic
from .common_schema import PageParam


class Routes(RoutesPydantic):
    meta: RouteMetaPydantic


class RoutesTo(Routes):
    """routes res"""

    children: List[Routes]
