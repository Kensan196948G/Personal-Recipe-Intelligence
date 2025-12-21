"""
Personal Recipe Intelligence - Database Configuration
"""

from sqlalchemy import event
from sqlmodel import Session, SQLModel, create_engine

from backend.core.config import settings

# Create engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, connection_record) -> None:
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA cache_size=-10000")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def create_db_and_tables():
    """データベースとテーブルを作成"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """セッションを取得"""
    with Session(engine) as session:
        yield session
