from datetime import datetime

from sqlalchemy import BigInteger, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from db.base_class import Base


class Analytics(Base):
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey('user.id', ondelete='SET NULL'),
        nullable=True, index=True
    )
    period = Column(String, nullable=False, index=True)
    period_from = Column(DateTime, nullable=True, index=True)
    period_to = Column(DateTime, nullable=True, index=True)
    status = Column(String, nullable=False, default='pending', index=True)
    html_path = Column(String, nullable=True)
    xlsx_path = Column(String, nullable=True)
    html_filename = Column(String, nullable=True)
    xlsx_filename = Column(String, nullable=True)
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    finished_at = Column(DateTime, nullable=True)

    user = relationship('User', lazy='joined')
