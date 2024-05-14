from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, Boolean  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

# if TYPE_CHECKING:
#     from .reg import Reg  # noqa: F401


class Service(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    alias = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    color_bg = Column(String, default='#d9d9d9')
    color_txt = Column(String, default='#424242')
    is_active = Column(Boolean, default=True, index=True)
    # regs = relationship('Reg', back_populates='number', lazy='joined')
