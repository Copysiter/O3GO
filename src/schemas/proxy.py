from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, field_serializer


# Shared properties
class ProxyBase(BaseModel):
    name: Optional[str] = None
    group_id: Optional[int] = None
    url: Optional[str] = None
    good_count: Optional[int] = None
    bad_count: Optional[int] = None
    info_1: Optional[str] = None
    info_2: Optional[str] = None
    info_3: Optional[str] = None
    int_1: Optional[int] = None
    int_2: Optional[int] = None
    int_3: Optional[int] = None
    ts_1: Optional[datetime] = None
    ts_2: Optional[datetime] = None
    ts_3: Optional[datetime] = None


# Properties to receive via API on creation
class ProxyCreate(ProxyBase):
    url: str


# Properties to receive via API on update
class ProxyUpdate(ProxyBase):
    pass


class ProxyInDBBase(ProxyBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
class Proxy(ProxyInDBBase):
    group: Optional['ProxyGroup'] = None

    class Config:
        from_attributes = True


# Additional properties stored in DB
class ProxyInDB(ProxyInDBBase):
    pass


# List of proxies to return via API
class ProxyRows(BaseModel):
    data: List[Proxy]
    total: int


class ProxyIds(BaseModel):
    ids: List[int]
