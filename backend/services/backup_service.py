"""
SQLite データベースバックアップサービス

自動バックアップ、世代管理、圧縮、リストア機能を提供する。
"""

import gzip
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel


class BackupInfo(BaseModel):
    """バックアップ情報モデル"""

    backup_id: str
    filename: str
    filepath: str
    size_bytes: int
    size_mb: float
    created_at: str
    is_compressed: bool


class BackupStatus(BaseModel):
    """バックアップ状態モデル"""

    total_backups: int
    total_size_mb: float
    oldest_backup: Optional[str]
    latest_backup: Optional[str]
    backup_dir: str


class BackupService:
    """SQLite データベースバックアップサービス"""

    def __init__(
        self,
        db_path: str,
        backup_dir: str = "data/backups",
        max_generations: int = 10,
        compress: bool = True,
    ):
        """
        バックアップサービスの初期化

        Args:
            db_path: バックアップ対象のデータベースファイルパス
            backup_dir: バックアップファイル保存ディレクトリ
            max_generations: 保持する最大世代数
            compress: gzip圧縮を行うか
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.max_generations = max_generations
        self.compress = compress

        # バックアップディレクトリが存在しない場合は作成
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, backup_name: Optional[str] = None) -> BackupInfo:
        """
        データベースのバックアップを作成

        Args:
            backup_name: バックアップファイル名（Noneの場合はタイムスタンプを使用）

        Returns:
            BackupInfo: 作成されたバックアップの情報

        Raises:
            FileNotFoundError: データベースファイルが存在しない場合
            IOError: バックアップ作成に失敗した場合
        """
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database file not found: {self.db_path}")

        # バックアップファイル名の生成
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if backup_name is None:
            backup_name = f"backup_{timestamp}.db"
        elif not backup_name.endswith(".db"):
            backup_name = f"{backup_name}_{timestamp}.db"

        backup_path = self.backup_dir / backup_name

        try:
            # データベースファイルをコピー
            shutil.copy2(self.db_path, backup_path)

            # 圧縮が有効な場合
            if self.compress:
                compressed_path = Path(f"{backup_path}.gz")
                with open(backup_path, "rb") as f_in:
                    with gzip.open(compressed_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)

                # 元の非圧縮ファイルを削除
                backup_path.unlink()
                backup_path = compressed_path

            # 世代管理を実行
            self._manage_generations()

            # バックアップ情報を取得
            return self._get_backup_info(backup_path)

        except Exception as e:
            # エラー時はバックアップファイルを削除
            if backup_path.exists():
                backup_path.unlink()
            if self.compress and Path(f"{backup_path}.gz").exists():
                Path(f"{backup_path}.gz").unlink()
            raise IOError(f"Failed to create backup: {str(e)}") from e

    def list_backups(self) -> List[BackupInfo]:
        """
        バックアップファイル一覧を取得

        Returns:
            List[BackupInfo]: バックアップ情報のリスト（作成日時の降順）
        """
        backups = []

        for file_path in self.backup_dir.glob("backup_*.db*"):
            try:
                backup_info = self._get_backup_info(file_path)
                backups.append(backup_info)
            except Exception:
                # 破損ファイルはスキップ
                continue

        # 作成日時の降順でソート
        backups.sort(key=lambda x: x.created_at, reverse=True)
        return backups

    def restore_backup(self, backup_id: str) -> bool:
        """
        バックアップからデータベースをリストア

        Args:
            backup_id: リストアするバックアップのID（ファイル名）

        Returns:
            bool: リストアが成功したか

        Raises:
            FileNotFoundError: 指定されたバックアップが存在しない場合
            IOError: リストアに失敗した場合
        """
        backup_path = self.backup_dir / backup_id

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_id}")

        try:
            # 現在のデータベースのバックアップを作成（安全のため）
            safety_backup = (
                self.backup_dir
                / f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            shutil.copy2(self.db_path, safety_backup)

            # 圧縮ファイルの場合は解凍してリストア
            if backup_path.suffix == ".gz":
                with gzip.open(backup_path, "rb") as f_in:
                    with open(self.db_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
            else:
                shutil.copy2(backup_path, self.db_path)

            return True

        except Exception as e:
            # エラー時は元に戻す
            if safety_backup.exists():
                shutil.copy2(safety_backup, self.db_path)
            raise IOError(f"Failed to restore backup: {str(e)}") from e

    def delete_backup(self, backup_id: str) -> bool:
        """
        バックアップファイルを削除

        Args:
            backup_id: 削除するバックアップのID（ファイル名）

        Returns:
            bool: 削除が成功したか

        Raises:
            FileNotFoundError: 指定されたバックアップが存在しない場合
        """
        backup_path = self.backup_dir / backup_id

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_id}")

        backup_path.unlink()
        return True

    def get_status(self) -> BackupStatus:
        """
        バックアップ状態を取得

        Returns:
            BackupStatus: バックアップの状態情報
        """
        backups = self.list_backups()

        total_size = sum(b.size_bytes for b in backups)
        oldest = backups[-1].created_at if backups else None
        latest = backups[0].created_at if backups else None

        return BackupStatus(
            total_backups=len(backups),
            total_size_mb=round(total_size / (1024 * 1024), 2),
            oldest_backup=oldest,
            latest_backup=latest,
            backup_dir=str(self.backup_dir.absolute()),
        )

    def _manage_generations(self) -> None:
        """
        バックアップの世代管理

        最大世代数を超えた古いバックアップを削除する。
        """
        backups = self.list_backups()

        if len(backups) > self.max_generations:
            # 古いバックアップを削除
            for backup in backups[self.max_generations :]:
                try:
                    self.delete_backup(backup.backup_id)
                except Exception:
                    # 削除失敗は無視
                    pass

    def _get_backup_info(self, file_path: Path) -> BackupInfo:
        """
        バックアップファイルの情報を取得

        Args:
            file_path: バックアップファイルのパス

        Returns:
            BackupInfo: バックアップ情報
        """
        stat = file_path.stat()
        size_bytes = stat.st_size
        created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()

        return BackupInfo(
            backup_id=file_path.name,
            filename=file_path.name,
            filepath=str(file_path.absolute()),
            size_bytes=size_bytes,
            size_mb=round(size_bytes / (1024 * 1024), 2),
            created_at=created_at,
            is_compressed=file_path.suffix == ".gz",
        )
