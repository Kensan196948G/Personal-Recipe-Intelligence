"""
Personal Recipe Intelligence - Configuration
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "Personal Recipe Intelligence"
    app_version: str = "0.1.0"
    debug: bool = False
    app_env: str = "development"

    # Database
    database_url: str = "sqlite:///./data/pri.db"

    # API
    api_v1_prefix: str = "/api/v1"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # CORS
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # DeepL API
    deepl_api_key: str = ""

    # Paths
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "data"
    logs_dir: Path = base_dir / "logs"


settings = Settings()
