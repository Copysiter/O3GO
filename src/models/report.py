from typing import TYPE_CHECKING
from datetime import date, datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, DateTime, Date, Index  # noqa
from sqlalchemy.orm import relationship

from db.base_class import Base  # noqa

if TYPE_CHECKING:
    from .device import Device  # noqa: F401


class Report(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    api_key = Column(String, index=True)
    device_id = Column(
        BigInteger, ForeignKey('device.id', ondelete='CASCADE')
    )
    service_id = Column(
        BigInteger, ForeignKey('service.id', ondelete='CASCADE')
    )
    start_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    number_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    code_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    no_code_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    waiting_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    bad_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    error_1_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    error_2_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    account_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    account_ban_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    sent_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    delivered_count = Column(
        Integer, nullable=False, server_default='0', default=0
    )
    date = Column(
        Date, nullable=False, default=date.today, index=True
    )
    timestamp = Column(
        DateTime, nullable=False,
        default=datetime.utcnow, onupdate=datetime.utcnow
    )
    info_1 = Column(String)
    info_2 = Column(String)
    info_3 = Column(String)
    int_1 = Column(Integer)
    int_2 = Column(Integer)
    int_3 = Column(Integer)
    ts_1 = Column(DateTime)
    ts_2 = Column(DateTime)
    ts_3 = Column(DateTime)

    device = relationship('Device', back_populates='reports', lazy='joined')

    ix_report_unique = Index(
        'ix_report_unique',
        api_key, device_id, service_id, date
    )
