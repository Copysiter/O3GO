from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, Integer, BigInteger, String, DateTime  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

# if TYPE_CHECKING:
#     from .reg import Reg  # noqa: F401


class Proxy(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, nullable=False, unique=True, index=True)
    good_count = Column(Integer, default=0)
    bad_count = Column(Integer, default=0)
    timestamp = Column(DateTime, nullable=False,
                       default=datetime.utcnow, onupdate=datetime.utcnow)
    # regs = relationship('Reg', back_populates='number', lazy='joined')
