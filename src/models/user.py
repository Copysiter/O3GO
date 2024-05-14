from sqlalchemy import Boolean, Column, Integer, String  # noqa

from db.base_class import Base  # noqa


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(125), index=True)
    login = Column(String(125), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean(), default=True)
    is_superuser = Column(Boolean(), default=False)
