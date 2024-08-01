from typing import TYPE_CHECKING
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, DateTime  # noqa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import AssociationProxy

from db.base_class import Base  # noqa

# if TYPE_CHECKING:
#     from .reg import Reg  # noqa: F401


class ProxyApiKeys(Base):
    __table_args__ = {'extend_existing': True}
    proxy_id = Column(BigInteger, ForeignKey(
        'proxy.id', ondelete='CASCADE'), primary_key=True)
    api_key = Column(String, primary_key=True)

    proxy = relationship('Proxy', back_populates='keys')


class Proxy(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
    url = Column(String, nullable=False, unique=True, index=True)
    good_count = Column(Integer, default=0)
    bad_count = Column(Integer, default=0)
    timestamp = Column(DateTime, nullable=False,
                       default=datetime.utcnow, onupdate=datetime.utcnow)
    info_1 = Column(String)
    info_2 = Column(String)
    info_3 = Column(String)
    int_1 = Column(Integer)
    int_2 = Column(Integer)
    int_3 = Column(Integer)
    ts_1 = Column(DateTime)
    ts_2 = Column(DateTime)
    ts_3 = Column(DateTime)
    # regs = relationship('Reg', back_populates='number', lazy='joined')

    keys = relationship(
        'ProxyApiKeys', back_populates='proxy', lazy='joined',
        cascade='save-update, merge, delete, delete-orphan'
    )
    api_keys = AssociationProxy('keys', 'api_key')
