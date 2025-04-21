from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, DateTime  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

if TYPE_CHECKING:
    from .reg import Reg  # noqa: F401
    from .service import Service  # noqa: F401
    from .device import Device  # noqa: F401


class Number(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    number = Column(String, nullable=False, unique=True, index=True)
    api_key = Column(String, index=True)
    service_alias = Column(String,
                           ForeignKey('service.alias', ondelete='CASCADE'))
    device_ext_id = Column(String,
                           ForeignKey('device.ext_id', ondelete='CASCADE'))
    setting_group_id = Column(BigInteger,
                           ForeignKey('setting_group.id', ondelete='CASCADE'))
    proxy = Column(String, index=True)
    timestamp = Column(
        DateTime, nullable=False, default=datetime.utcnow, index=True)
    info_1 = Column(String, index=True)
    info_2 = Column(String, index=True)
    info_3 = Column(String, index=True)
    info_4 = Column(String, index=True)
    info_5 = Column(String, index=True)
    info_6 = Column(String, index=True)

    setting_group = relationship('SettingGroup', back_populates='numbers', lazy='joined')
    regs = relationship('Reg', back_populates='number', lazy='joined')
