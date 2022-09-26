import logging

from sqlalchemy import Column, Integer, String

from group_bot.models.base import Base, current_time

logger = logging.getLogger(__name__)


class TrxProgress(Base):
    """the progress trx_id of rum groups"""

    __tablename__ = "trx_progress"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    progress_type = Column(String(36))
    trx_id = Column(String(36), default=None)
    timestamp = Column(String)  # the timestamp of the trx
    created_at = Column(String, default=current_time)
    updated_at = Column(String, default=current_time)

    def __init__(self, obj):
        super().__init__(**obj)
