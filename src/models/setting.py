from datetime import datetime

from sqlalchemy import (
    Column, ForeignKey, Integer, SmallInteger,
    BigInteger, String, Text, DateTime, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.associationproxy import AssociationProxy

from db.base_class import Base


class SettingGroupApiKeys(Base):
    __table_args__ = {'extend_existing': True}
    group_id = Column(BigInteger, ForeignKey(
        'setting_group.id', ondelete='CASCADE'), primary_key=True
    )
    api_key = Column(String, primary_key=True)

    group = relationship('SettingGroup', back_populates='keys')


class Setting(Base):
    """Справочник параметров (настроек)"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255))
    key = Column(String(255), nullable=False, index=True, unique=True)
    type = Column(SmallInteger, nullable=False)
    proxy_group_default = Column(
        BigInteger, ForeignKey('proxy_group.id', ondelete='CASCADE')
    )
    str_default = Column(String, nullable=True)
    int_default = Column(Integer, nullable=True)
    bool_default = Column(Boolean, nullable=True)
    description = Column(Text, nullable=True)
    order = Column(Integer, index=True)
    is_active = Column(Boolean, default=True, index=True)

    proxy_group = relationship(
        'ProxyGroup',
        back_populates='settings'
    )
    options = relationship(
        'SettingOption',
        back_populates='setting',
        cascade='all, delete-orphan',
        lazy='select'
    )
    values = relationship(
        'SettingValue',
        back_populates='setting',
        cascade='all, delete-orphan',
        lazy='select'
    )


class SettingOption(Base):
    """Вариант значения параметра, если тип dropdown"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), index=True)
    value = Column(String(255), nullable=False, index=True)
    setting_id = Column(
        BigInteger, ForeignKey('setting.id', ondelete='CASCADE')
    )

    setting = relationship('Setting', back_populates='options')


class SettingGroup(Base):
    """Группа настроек (конкретные значения параметров)"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    service = Column(
        String, ForeignKey('service.alias', ondelete='SET NULL'),
        nullable=True, index=True
    )

    check_period = Column(Integer, index=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    values = relationship(
        'SettingValue',
        back_populates='group',
        cascade='all, delete-orphan',
        lazy='select'
    )
    keys = relationship(
        'SettingGroupApiKeys',
        back_populates='group',
        cascade='save-update, merge, delete, delete-orphan',
        lazy='select'
    )
    service_obj = relationship('Service', lazy='select')
    api_keys = AssociationProxy('keys', 'api_key')


class SettingValue(Base):
    """Конкретное значение параметра в группе"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(
        BigInteger, ForeignKey('setting_group.id', ondelete='CASCADE'))
    setting_id = Column(
        BigInteger, ForeignKey('setting.id', ondelete='CASCADE')
    )
    proxy_group_id = Column(
        BigInteger, ForeignKey('proxy_group.id', ondelete='CASCADE')
    )
    str_val = Column(String, nullable=True)
    int_val = Column(Integer, nullable=True)
    bool_val = Column(Boolean, nullable=True)

    group = relationship(
        'SettingGroup',
        back_populates='values'
    )
    setting = relationship('Setting', lazy='select')
    proxy_group = relationship('ProxyGroup', lazy='select')
