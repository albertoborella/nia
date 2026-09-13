from collections.abc import Generator

from sqlmodel import SQLModel, Session, create_engine

from app.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
