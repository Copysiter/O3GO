from typing import List, Optional, Literal  # noqa
from datetime import datetime

from pydantic import BaseModel

from .reg import Reg
from .setting import SettingGroup


# Shared properties
class NumberBase(BaseModel):
    number: Optional[str] = None
    service_alias: Optional[str] = None
    proxy: Optional[str] = None
    device_ext_id: Optional[str] = None
    setting_group_id: Optional[int] = None
    api_key: str
    info_1: Optional[str] = None
    info_2: Optional[str] = None
    info_3: Optional[str] = None
    info_4: Optional[str] = None
    info_5: Optional[str] = None
    info_6: Optional[str] = None


# Properties to receive on number creation
class NumberCreate(NumberBase):
    number: str
    service_alias: str


# Properties to receive on number update
class NumberUpdate(NumberBase):
    pass


# Properties shared by models stored in DB
class NumberInDBBase(NumberBase):
    id: int
    timestamp: Optional[datetime] = datetime.utcnow()

    class Config:
        from_attributes = True


# Properties to return to client
class Number(NumberInDBBase):
    regs: List[Reg]
    setting_group: Optional[SettingGroup]


class NumberInDB(NumberInDBBase):
    pass


# List of numbers to return via API
class NumberRows(BaseModel):
    data: List[Number]
    total: int


class NumberFilter(BaseModel):
    where_service: Optional[str] = None
    where_proxy: Optional[str] = None
    where_device_id: Optional[str] = None
    where_api_key: Optional[str] = None
    where_info_1: Optional[str] = None
    where_info_2: Optional[str] = None
    where_info_3: Optional[str] = None
    where_info_4: Optional[str] = None
    where_info_5: Optional[str] = None
    where_info_6: Optional[str] = None
