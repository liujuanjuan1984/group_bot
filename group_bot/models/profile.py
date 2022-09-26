import logging

from sqlalchemy import Column, Integer, String

from group_bot.models.base import Base, current_time

logger = logging.getLogger(__name__)


class Profile(Base):
    """the users profiles in rum groups."""

    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    pubkey = Column(String(36), index=True)
    name = Column(String(36))
    wallet = Column(String, default=None)
    timestamp = Column(String)
    created_at = Column(String, default=current_time)
    updated_at = Column(String, default=current_time)

    def __init__(self, obj):
        super().__init__(**obj)
