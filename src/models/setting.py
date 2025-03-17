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
        'setting_group.id', ondelete='CASCADE'), primary_key=True)
    api_key = Column(String, primary_key=True)

    group = relationship('SettingGroup', back_populates='keys')


class Setting(Base):
    """Справочник параметров (настроек)"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    key = Column(String(255), nullable=False, index=True, unique=True)
    type = Column(SmallInteger, nullable=False)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, index=True)

    options = relationship(
        'SettingOption',
        back_populates='setting',
        cascade='all, delete-orphan',
        lazy='joined'
    )
    values = relationship(
        'SettingValue',
        back_populates='setting',
        cascade='all, delete-orphan',
        lazy='joined'
    )


class SettingOption(Base):
    """Вариант значения параметра, если тип dropdown"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    setting_id = Column(
        BigInteger, ForeignKey('setting.id', ondelete='CASCADE'))
    value = Column(String(255), nullable=False)

    setting = relationship('Setting', back_populates='options')


class SettingGroup(Base):
    """Группа настроек (конкретные значения параметров)"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    is_active = Column(Boolean, default=True, index=True)

    values = relationship(
        'SettingValue',
        back_populates='group',
        cascade='all, delete-orphan',
        lazy='joined'
    )
    keys = relationship(
        'SettingGroupApiKeys',
        back_populates='group',
        cascade='save-update, merge, delete, delete-orphan',
        lazy='joined', join_depth=1
    )
    api_keys = AssociationProxy('keys', 'api_key')
    numbers = relationship('Number', back_populates='setting_group')


class SettingValue(Base):
    """Конкретное значение параметра в группе"""
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    group_id = Column(
        BigInteger, ForeignKey('setting_group.id', ondelete='CASCADE'))
    setting_id = Column(
        BigInteger, ForeignKey('setting.id', ondelete='CASCADE'))
    proxy_group_id = Column(
        BigInteger, ForeignKey('proxy_group.id', ondelete='CASCADE'))
    str_val = Column(String, nullable=True)
    int_val = Column(Integer, nullable=True)
    bool_val = Column(Boolean, nullable=True)

    group = relationship(
        'SettingGroup',
        back_populates='values'
    )
    setting = relationship(
        'Setting',
        back_populates='values',
        lazy='joined'
    )
    proxy_group = relationship(
        'ProxyGroup',
        back_populates='values',
        lazy='joined'
    )
