"""
バックアップサービス設定例

環境に応じて設定値を調整してください。
"""

from pathlib import Path

# データベース設定
DATABASE_PATH = "data/recipes.db"

# バックアップディレクトリ
BACKUP_DIR = "data/backups"

# 最大世代数（古いバックアップは自動削除される）
MAX_BACKUP_GENERATIONS = 10

# gzip 圧縮を有効にするか
ENABLE_COMPRESSION = True

# 自動バックアップ設定（将来実装予定）
AUTO_BACKUP_ENABLED = False
AUTO_BACKUP_INTERVAL_HOURS = 24  # 24時間ごと
AUTO_BACKUP_TIME = "03:00"  # 午前3時に実行

# バックアップファイル名のプレフィックス
BACKUP_PREFIX = "backup"

# 安全バックアップのプレフィックス（リストア前の自動バックアップ）
SAFETY_BACKUP_PREFIX = "pre_restore"

# バックアップディレクトリの自動作成
AUTO_CREATE_BACKUP_DIR = True

# ログ設定
LOG_BACKUP_OPERATIONS = True
LOG_FILE_PATH = "logs/backup.log"


def get_backup_config() -> dict:
    """
    バックアップ設定を辞書形式で取得

    Returns:
        dict: バックアップ設定
    """
    return {
        "db_path": DATABASE_PATH,
        "backup_dir": BACKUP_DIR,
        "max_generations": MAX_BACKUP_GENERATIONS,
        "compress": ENABLE_COMPRESSION,
        "auto_backup_enabled": AUTO_BACKUP_ENABLED,
        "auto_backup_interval_hours": AUTO_BACKUP_INTERVAL_HOURS,
        "auto_backup_time": AUTO_BACKUP_TIME,
    }


def validate_config() -> bool:
    """
    設定値の妥当性をチェック

    Returns:
        bool: 設定が有効か

    Raises:
        ValueError: 設定値が不正な場合
    """
    # データベースファイルの存在確認
    db_path = Path(DATABASE_PATH)
    if not db_path.exists():
        raise ValueError(f"Database file not found: {DATABASE_PATH}")

    # バックアップディレクトリの作成
    backup_dir = Path(BACKUP_DIR)
    if not backup_dir.exists() and AUTO_CREATE_BACKUP_DIR:
        backup_dir.mkdir(parents=True, exist_ok=True)

    # 最大世代数の妥当性チェック
    if MAX_BACKUP_GENERATIONS < 1:
        raise ValueError("MAX_BACKUP_GENERATIONS must be at least 1")

    return True
