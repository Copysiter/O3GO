from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel


# Shared properties
class ReportBase(BaseModel):
    api_key: Optional[str] = None
    device_id: Optional[int] = None
    service_id: Optional[int] = None
    start_count: Optional[int] = 0
    number_count: Optional[int] = 0
    code_count: Optional[int] = 0
    no_code_count: Optional[int] = 0
    bad_count: Optional[int] = 0


# Properties to receive via API on creation
class ReportCreate(ReportBase):
    api_key: str
    device_id: int
    service_id: int


# Properties to receive via API on update
class ReportUpdate(ReportBase):
    pass


class ReportInDBBase(ReportBase):
    id: int
    date: date
    timestamp: datetime

    class Config:
        from_attributes = True


# Additional properties to return via API
class Report(ReportInDBBase):
    pass


# Additional properties stored in DB
class ReportInDB(ReportInDBBase):
    pass


# List of reports to return via API
class ReportRows(BaseModel):
    data: List[Report]
    total: int
