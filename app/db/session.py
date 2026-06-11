from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


def create_db_engine():
    return create_engine(settings.DATABASE_URL, echo=settings.APP_DEBUG)


def create_session_factory(engine):
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


engine = create_db_engine()
SessionLocal = create_session_factory(engine)
