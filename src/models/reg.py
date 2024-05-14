from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, DateTime  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

if TYPE_CHECKING:
    from .number import Number  # noqa: F401


class Reg(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    number_id = Column(BigInteger, ForeignKey('number.id'))
    service = Column(String, index=True)
    timestamp = Column(
        DateTime, nullable=False, default=datetime.utcnow, index=True)

    number = relationship('Number', back_populates='regs')
