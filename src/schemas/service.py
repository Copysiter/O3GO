from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class ServiceBase(BaseModel):
    alias: Optional[str] = None
    name: Optional[str] = None
    color_bg: Optional[str] = '#d9d9d9'
    color_txt: Optional[str] = '#424242'
    is_active: Optional[bool] = True


# Properties to receive via API on creation
class ServiceCreate(ServiceBase):
    alias: str


# Properties to receive via API on update
class ServiceUpdate(ServiceBase):
    pass


class ServiceInDBBase(ServiceBase):
    id: int

    class Config:
        from_attributes = True


# Additional properties to return via API
class Service(ServiceInDBBase):
    pass


# Additional properties stored in DB
class ServiceInDB(ServiceInDBBase):
    pass


# List of services to return via API
class ServiceRows(BaseModel):
    data: List[Service]
    total: int
