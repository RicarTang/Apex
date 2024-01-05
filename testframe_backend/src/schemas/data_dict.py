from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from ..db.enum import BoolEnum
from ..schemas.common import PageParam, DefaultModel


class DataDictIn(BaseModel):
    dict_type: str = Field(alias="dictType", description="字典类型")
    dict_label: str = Field(alias="dictLabel", description="字典label")
    dict_value: str = Field(alias="dictValue", description="字典值")
    list_class: Optional[str] = Field(
        default=None, alias="listClass", description="css属性"
    )
    css_class: Optional[str] = Field(
        default=None, alias="cssClass", description="css类名"
    )
    is_default: BoolEnum = Field(description="是否是默认选项")
    remark: Optional[str] = Field(default=None, description="备注")


class DataDictTo(DefaultModel):
    """字典数据res schema"""
    model_config = ConfigDict(from_attributes=True)

    dict_type: str = Field(serialization_alias="dictType", description="字典类型")
    dict_label: str = Field(serialization_alias="dictLabel", description="字典label")
    dict_value: str = Field(serialization_alias="dictValue", description="字典值")
    list_class: Optional[str] = Field(
        default=None, serialization_alias="listClass", description="css属性"
    )
    css_class: Optional[str] = Field(
        default=None, serialization_alias="cssClass", description="css类名"
    )
    is_default: BoolEnum = Field(description="是否是默认选项",serialization_alias="isDefault")
    remark: Optional[str] = Field(default=None, description="备注")


class DataDictsTo(PageParam):
    data: List[DataDictTo]
