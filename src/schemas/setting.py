from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, field_serializer
from dataclasses import dataclass

from .enum import Enum
from .proxy_group import ProxyGroup


@dataclass
class Type(Enum):
    TEXT: int = 0
    INTEGER: int = 1
    BOOLEAN: int = 2
    DROPDOWN: int = 3
    PROXY: int = 4


class SettingOption(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    value: str
    setting_id: int

    class Config:
        from_attributes = True


# Shared properties
class SettingBase(BaseModel):
    name: Optional[str] = None
    key: Optional[str] = None
    type: Optional[int] = None
    proxy_group_default: Optional[int] = None
    str_default: Optional[str] = None
    int_default: Optional[int] = None
    bool_default: Optional[bool] = None
    description: Optional[str] = None
    options: Optional[str] = ''
    order: Optional[int] = None
    is_active: Optional[bool] = None


# Properties to receive via API on creation
class SettingCreate(SettingBase):
    key: str
    type: int


# Properties to receive via API on update
class SettingUpdate(SettingBase):
    pass


class SettingInDBBase(SettingBase):
    id: int

    class Config:
        from_attributes = True


# Additional properties to return via API
class Setting(SettingInDBBase):
    options: List[SettingOption] = []

    @field_serializer("options")
    def serialize_options(self, options: List[SettingOption]) -> str:
        return '\n'.join(
            f'{option.name or option.value} | {option.value}' for option in options
        )


# Additional properties stored in DB
class SettingInDB(SettingInDBBase):
    pass


# List of reports to return via API
class SettingRows(BaseModel):
    data: List[Setting]
    total: int


class SettingValue(BaseModel):
    id: int
    group_id: int
    setting_id: int
    proxy_group_id: Optional[int] = None
    str_val: Optional[str] = None
    int_val: Optional[int] = None
    bool_val: Optional[bool] = None
    setting: Setting
    proxy_group: Optional[ProxyGroup] = None

    class Config:
        from_attributes = True


class SettingGroupBase(BaseModel):
    name: Optional[str] = None
    service: Optional[str] = None
    check_period: Optional[int] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


# Properties to receive via API on creation
class SettingGroupCreate(SettingGroupBase):
    name: str
    api_keys: list = []

    class Config:
        extra = 'allow'


# Properties to receive via API on update
class SettingGroupUpdate(SettingGroupBase):
    api_keys: list = []

    class Config:
        extra = 'allow'

class SettingGroupInDBBase(SettingGroupBase):
    id: int
    timestamp: Optional[datetime]

    class Config:
        from_attributes = True


# Additional properties to return via API
class SettingGroup(SettingGroupInDBBase):
    values: List[SettingValue] = []
    api_keys: List[str] = []

    class Config:
        extra = 'allow'


# Additional properties stored in DB
class SettingGroupInDB(SettingGroupInDBBase):
    pass


# List of reports to return via API
class SettingGroupRows(BaseModel):
    data: List[SettingGroup]
    total: int


class SettingGroupIds(BaseModel):
    ids: List[int]


class SettingGroupStatusIds(BaseModel):
    ids: List[int]
    is_active: bool