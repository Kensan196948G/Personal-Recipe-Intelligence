"""
バックアップサービスのテスト

SQLite データベースのバックアップ、リストア、世代管理機能をテストする。
"""

import gzip
import shutil
import tempfile
from pathlib import Path

import pytest

from backend.services.backup_service import BackupInfo, BackupService, BackupStatus


@pytest.fixture
def temp_db():
    """テスト用の一時データベースファイルを作成"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
        # ダミーデータを書き込む
        f.write(b"test database content")
    yield db_path
    # クリーンアップ
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def temp_backup_dir():
    """テスト用の一時バックアップディレクトリを作成"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # クリーンアップ
    if temp_dir.exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def backup_service(temp_db, temp_backup_dir):
    """バックアップサービスインスタンスを作成"""
    return BackupService(
        db_path=str(temp_db),
        backup_dir=str(temp_backup_dir),
        max_generations=5,
        compress=True,
    )


def test_create_backup(backup_service):
    """バックアップ作成のテスト"""
    backup_info = backup_service.create_backup()

    assert backup_info is not None
    assert isinstance(backup_info, BackupInfo)
    assert backup_info.backup_id.startswith("backup_")
    assert backup_info.is_compressed is True
    assert backup_info.size_bytes > 0


def test_create_backup_with_custom_name(backup_service):
    """カスタム名でのバックアップ作成テスト"""
    backup_info = backup_service.create_backup(backup_name="custom_backup")

    assert backup_info is not None
    assert "custom_backup" in backup_info.backup_id
    assert backup_info.backup_id.endswith(".db.gz")


def test_list_backups(backup_service):
    """バックアップ一覧取得のテスト"""
    # バックアップを1つ作成
    backup_service.create_backup()

    backups = backup_service.list_backups()

    # 少なくとも1つのバックアップが存在
    assert len(backups) >= 1
    assert all(isinstance(b, BackupInfo) for b in backups)
    # 作成日時の降順でソートされていることを確認
    if len(backups) >= 2:
        assert backups[0].created_at >= backups[1].created_at


def test_restore_backup(backup_service, temp_db):
    """バックアップリストアのテスト"""
    # バックアップを作成
    backup_info = backup_service.create_backup()

    # データベースファイルを変更
    with open(temp_db, "wb") as f:
        f.write(b"modified content")

    # リストアを実行
    success = backup_service.restore_backup(backup_info.backup_id)

    assert success is True

    # 元のデータに戻っているか確認
    with open(temp_db, "rb") as f:
        content = f.read()
    assert content == b"test database content"


def test_delete_backup(backup_service):
    """バックアップ削除のテスト"""
    # バックアップを作成
    backup_info = backup_service.create_backup()

    # バックアップが存在することを確認
    backups = backup_service.list_backups()
    assert len(backups) == 1

    # バックアップを削除
    success = backup_service.delete_backup(backup_info.backup_id)

    assert success is True

    # バックアップが削除されたことを確認
    backups = backup_service.list_backups()
    assert len(backups) == 0


def test_delete_nonexistent_backup(backup_service):
    """存在しないバックアップの削除テスト"""
    with pytest.raises(FileNotFoundError):
        backup_service.delete_backup("nonexistent_backup.db.gz")


def test_generation_management(backup_service):
    """世代管理のテスト"""
    # max_generations(5) を超えるバックアップを作成
    for i in range(7):
        backup_service.create_backup()

    backups = backup_service.list_backups()

    # 最大世代数以内に収まっているか確認
    assert len(backups) <= 5


def test_get_status(backup_service):
    """バックアップ状態取得のテスト"""
    # バックアップを1つ作成
    backup_service.create_backup()

    status = backup_service.get_status()

    assert isinstance(status, BackupStatus)
    # 少なくとも1つ以上のバックアップがあることを確認
    assert status.total_backups >= 1
    assert status.total_size_mb >= 0
    assert status.oldest_backup is not None
    assert status.latest_backup is not None
    assert status.backup_dir is not None


def test_compression(backup_service, temp_backup_dir):
    """圧縮機能のテスト"""
    backup_info = backup_service.create_backup()

    # 圧縮ファイルが作成されているか確認
    backup_path = temp_backup_dir / backup_info.backup_id
    assert backup_path.exists()
    assert backup_path.suffix == ".gz"

    # 圧縮ファイルを解凍して内容を確認
    with gzip.open(backup_path, "rb") as f:
        content = f.read()
    assert content == b"test database content"


def test_create_backup_without_compression(temp_db, temp_backup_dir):
    """非圧縮バックアップ作成のテスト"""
    service = BackupService(
        db_path=str(temp_db), backup_dir=str(temp_backup_dir), compress=False
    )

    backup_info = service.create_backup()

    assert backup_info.is_compressed is False
    assert backup_info.backup_id.endswith(".db")

    # 非圧縮ファイルが作成されているか確認
    backup_path = temp_backup_dir / backup_info.backup_id
    assert backup_path.exists()


def test_restore_nonexistent_backup(backup_service):
    """存在しないバックアップのリストアテスト"""
    with pytest.raises(FileNotFoundError):
        backup_service.restore_backup("nonexistent_backup.db.gz")


def test_create_backup_with_nonexistent_db(temp_backup_dir):
    """存在しないデータベースのバックアップテスト"""
    service = BackupService(db_path="nonexistent.db", backup_dir=str(temp_backup_dir))

    with pytest.raises(FileNotFoundError):
        service.create_backup()
