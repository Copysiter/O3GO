from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, DateTime, Boolean  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

if TYPE_CHECKING:
    from .report import Report  # noqa: F401


class Device(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    ext_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    root = Column(Boolean, index=True)
    operator = Column(String, index=True)
    timestamp = Column(DateTime, nullable=False,
                       default=datetime.utcnow, onupdate=datetime.utcnow)
    reports = relationship('Report', back_populates='device')
