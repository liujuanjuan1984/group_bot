import datetime
import logging

from sqlalchemy import Column, Integer, String

from group_bot.models import Base

logger = logging.getLogger(__name__)


class MsgStatus(Base):
    """the status of message, each message can have many status, but only one status for one message"""

    __tablename__ = "message_status"

    id = Column(Integer, unique=True, primary_key=True, index=True)
    message_id = Column(String(36))
    status = Column(String, default=None)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)
