from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, BigInteger, String, DateTime, text, desc  # noqa
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import AssociationProxy

from db.base_class import Base  # noqa


class ProxyApiKeys(Base):
    __table_args__ = {'extend_existing': True}
    proxy_id = Column(BigInteger, ForeignKey(
        'proxy.id', ondelete='CASCADE'), primary_key=True)
    api_key = Column(String, primary_key=True)

    proxy = relationship('Proxy', back_populates='keys')


class ProxyGroup(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)

    proxies = relationship(
        'Proxy',
        back_populates='group',
        cascade='all, delete-orphan',
        order_by='asc(Proxy.url)',
        lazy='joined'
    )
    settings = relationship(
        'Setting',
        back_populates='proxy_group',
        cascade='all, delete-orphan'
    )
    values = relationship(
        'SettingValue',
        back_populates='proxy_group',
        cascade='all, delete-orphan'
    )

class Proxy(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String, index=True)
    group_id = Column(BigInteger, ForeignKey('proxy_group.id', ondelete='CASCADE'))
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
        'ProxyApiKeys',
        back_populates='proxy',
        cascade='save-update, merge, delete, delete-orphan',
        lazy='joined'
    )
    group = relationship(
        'ProxyGroup',
        back_populates='proxies',
        lazy='joined'
    )
    api_keys = AssociationProxy('keys', 'api_key')
