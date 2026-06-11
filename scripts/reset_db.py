import argparse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base


def reset_db():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Database reset completed")


if __name__ == "__main__":
    reset_db()
