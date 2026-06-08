from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class AnalyticsBase(BaseModel):
    period: Optional[str] = None
    period_from: Optional[datetime] = None
    period_to: Optional[datetime] = None
    status: Optional[str] = None
    html_filename: Optional[str] = None
    xlsx_filename: Optional[str] = None
    error: Optional[str] = None
    created_by_id: Optional[int] = None
    finished_at: Optional[datetime] = None


class AnalyticsCreate(AnalyticsBase):
    period: str
    status: str = 'pending'


class AnalyticsUpdate(AnalyticsBase):
    pass


class AnalyticsInDBBase(AnalyticsBase):
    id: int
    period: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class Analytics(AnalyticsInDBBase):
    pass


class AnalyticsInDB(AnalyticsInDBBase):
    pass


class AnalyticsRows(BaseModel):
    data: List[Analytics]
    total: int


class AnalyticsRunRequest(BaseModel):
    period: str = 'Current selection'
    filters: List[dict[str, Any]] = Field(default_factory=list)


class AnalyticsIds(BaseModel):
    ids: List[int]
