from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .report import Report


# Shared properties
class DeviceBase(BaseModel):
    ext_id: Optional[str] = None
    name: Optional[str] = None
    root: Optional[bool] = True
    operator: Optional[str] = None
    api_key: Optional[str] = None


# Properties to receive via API on creation
class DeviceCreate(DeviceBase):
    ext_id: str


# Properties to receive via API on update
class DeviceUpdate(DeviceBase):
    pass


class DeviceInDBBase(DeviceBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
class Device(DeviceInDBBase):
    pass


# Additional properties stored in DB
class DeviceInDB(DeviceInDBBase):
    pass


# List of devices to return via API
class DeviceRows(BaseModel):
    data: List[Device]
    total: int
