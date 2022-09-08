import datetime
import logging

from sqlalchemy import Boolean, Column, Integer, String

from group_bot.models.base import Base

logger = logging.getLogger(__name__)


class KeyStore(Base):
    """each mixin_id got a keystore"""

    __tablename__ = "keystores"

    id = Column(Integer, primary_key=True, unique=True, index=True)
    user_id = Column(String(36), unique=True, index=True)  # mixin_id
    addr = Column(String, default=None)
    keystore = Column(String)
    is_rss = Column(Boolean, default=True)
    created_at = Column(String, default=str(datetime.datetime.now()))
    updated_at = Column(String, default=str(datetime.datetime.now()))

    def __init__(self, obj):
        super().__init__(**obj)
