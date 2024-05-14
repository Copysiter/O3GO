from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel


# Shared properties
class RegBase(BaseModel):
    number_id: int
    service: str


# Properties to receive on reg creation
class RegCreate(RegBase):
    pass


# Properties to receive on reg update
class RegUpdate(RegBase):
    pass


# Properties shared by models stored in DB
class RegInDBBase(RegBase):
    id: int
    timestamp: Optional[datetime] = datetime.utcnow()

    class Config:
        from_attributes = True


# Properties to return to client
class Reg(RegInDBBase):
    pass


# Additional properties stored in DB
class RegInDB(RegInDBBase):
    pass


# List of regs to return via API
class RegRows(BaseModel):
    data: List[Reg]
    total: int
