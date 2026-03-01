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
    waiting_count: Optional[int] = 0
    bad_count: Optional[int] = 0
    error_1_count: Optional[int] = 0
    error_2_count: Optional[int] = 0
    account_count: Optional[int] = 0
    account_ban_count: Optional[int] = 0
    sent_count: Optional[int] = 0
    delivered_count: Optional[int] = 0
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
