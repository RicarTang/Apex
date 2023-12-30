from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, ConfigDict
from ..db.models import Routes
from ..schemas.default import Routes
from ..utils.log_util import log


class TreeSelectTo(BaseModel):
    """树形菜单"""

    model_config = ConfigDict(from_attributes=True)
    id: Optional[int] = Field(default=None)
    label: Optional[str] = Field(
        default=None, validation_alias="meta", description="树形菜单label"
    )
    # children: Optional[List[Routes]] = Field(default=None)
    children: Optional[List["TreeSelectTo"]] = Field(default=None)

    @field_validator("label", mode="before")
    @classmethod
    def modify_label_before_validation(cls, value):
        """模型验证前修改入参"""
        log.debug(value)
        try:
            return value.title
        except AttributeError as e:
            # orm对象返回空，不做处理
            log.error(e)

    @field_validator("children", mode="before")
    @classmethod
    def modify_children_before_validation(cls, value):
        """模型验证前修改入参"""

        try:
            res = [Routes.from_orm(children) for children in value]
            return res
        except AttributeError as e:
            # orm对象返回空，不做处理
            log.error(e)
