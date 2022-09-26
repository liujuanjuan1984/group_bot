import logging

from sqlalchemy import Boolean, Column, Integer, String

from group_bot.models.base import Base, current_time

logger = logging.getLogger(__name__)


class Trx(Base):
    """trxs data from rum groups which waiting to be sent."""

    __tablename__ = "trxs"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    trx_id = Column(String(36), unique=True)
    text = Column(String)
    timestamp = Column(String, index=True)  # trx 的 timestamp
    is_sent = Column(Boolean, default=False, index=True)
    created_at = Column(String, default=current_time)
    updated_at = Column(String, default=current_time)

    def __init__(self, obj):
        super().__init__(**obj)
