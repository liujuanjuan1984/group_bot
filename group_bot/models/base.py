import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

logger = logging.getLogger(__name__)


class BaseDB:
    def __init__(self, db_name, echo=False, reset=False, init=False):
        # 创建数据库
        engine = create_engine(db_name, echo=echo, connect_args={"check_same_thread": False})
        if reset:
            Base.metadata.drop_all(engine)
        if init:
            # 创建表
            Base.metadata.create_all(engine)
        # 创建会话
        self.Session = sessionmaker(bind=engine, autoflush=False)
        self.session = self.Session()
        logger.debug(f"init db, name: {db_name}, echo: {echo}, reset: {reset}")

    def __commit(self, session=None):
        """Commits the current db.session, does rollback on failure."""
        from sqlalchemy.exc import IntegrityError

        logger.debug("db commit")
        session = session or self.session

        try:
            session.commit()
        except IntegrityError:
            session.rollback()

    def add(self, obj, session=None):
        """Adds this model to the db (through db.session)"""
        session = session or self.session
        session.add(obj)
        self.__commit(session)
        return self

    def commit(self):
        self.__commit()
        return self
