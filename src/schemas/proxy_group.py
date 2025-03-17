from typing import List, Optional, TYPE_CHECKING

from pydantic import BaseModel, field_serializer

from .proxy import Proxy


# Shared properties
class ProxyGroupBase(BaseModel):
    name: Optional[str] = None
    proxies: list = []


# Properties to receive via API on creation
class ProxyGroupCreate(ProxyGroupBase):
    proxies: Optional[str] = None


# Properties to receive via API on update
class ProxyGroupUpdate(ProxyGroupBase):
    proxies: Optional[str] = None


class ProxyGroupInDBBase(ProxyGroupBase):
    id: int

    class Config:
        from_attributes = True


# Additional properties to return via API
class ProxyGroup(ProxyGroupInDBBase):
    proxies: List[Proxy] = []

    class Config:
        from_attributes = True

    @field_serializer("proxies")
    def serialize_options(self, proxies: List[Proxy]) -> str:
        return "\n".join(proxy.url for proxy in proxies)


# Additional properties stored in DB
class ProxyGroupInDB(ProxyGroupInDBBase):
    pass


# List of proxies to return via API
class ProxyGroupRows(BaseModel):
    data: List[ProxyGroup]
    total: int
