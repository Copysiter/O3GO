from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class ProxyBase(BaseModel):
    name: Optional[str] = None
    url: Optional[str] = None
    good_count: Optional[int] = None
    bad_count: Optional[int] = None


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
    pass


# Additional properties stored in DB
class ProxyInDB(ProxyInDBBase):
    pass


# List of proxies to return via API
class ProxyRows(BaseModel):
    data: List[Proxy]
    total: int
