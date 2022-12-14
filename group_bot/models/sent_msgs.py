import logging

from sqlalchemy import Column, Integer, String

from group_bot.models.base import Base, current_time

logger = logging.getLogger(__name__)


class SentMsgs(Base):
    """the trx_id of message sent by bot."""

    __tablename__ = "sent_msgs"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    message_id = Column(String(36), index=True)  # of mixin
    trx_id = Column(String(36))  # of rum
    user_id = Column(String(36))  # of mixin
    created_at = Column(String, default=current_time)
    updated_at = Column(String, default=current_time)

    def __init__(self, obj):
        super().__init__(**obj)
