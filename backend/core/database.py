"""
Personal Recipe Intelligence - Database Configuration
"""
from sqlmodel import Session, SQLModel, create_engine

from backend.core.config import settings

# Create engine
engine = create_engine(
  settings.database_url,
  echo=settings.debug,
  connect_args={"check_same_thread": False}
)


def create_db_and_tables():
  """データベースとテーブルを作成"""
  SQLModel.metadata.create_all(engine)


def get_session():
  """セッションを取得"""
  with Session(engine) as session:
    yield session
