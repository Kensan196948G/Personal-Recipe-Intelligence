"""
バックアップ API ルーター

データベースのバックアップ、リストア、管理機能を提供する API エンドポイント。
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from backend.services.backup_service import BackupInfo, BackupService, BackupStatus


# APIレスポンスモデル
class APIResponse(BaseModel):
    """標準APIレスポンス"""

    status: str
    data: Optional[dict] = None
    error: Optional[str] = None


class CreateBackupRequest(BaseModel):
    """バックアップ作成リクエスト"""

    backup_name: Optional[str] = None


class CreateBackupResponse(BaseModel):
    """バックアップ作成レスポンス"""

    status: str
    data: BackupInfo
    error: Optional[str] = None


class ListBackupsResponse(BaseModel):
    """バックアップ一覧レスポンス"""

    status: str
    data: List[BackupInfo]
    error: Optional[str] = None


class RestoreBackupResponse(BaseModel):
    """バックアップリストアレスポンス"""

    status: str
    data: dict
    error: Optional[str] = None


class DeleteBackupResponse(BaseModel):
    """バックアップ削除レスポンス"""

    status: str
    data: dict
    error: Optional[str] = None


class StatusResponse(BaseModel):
    """バックアップ状態レスポンス"""

    status: str
    data: BackupStatus
    error: Optional[str] = None


# ルーター初期化
router = APIRouter(prefix="/api/v1/backup", tags=["backup"])

# バックアップサービスインスタンス（設定は環境変数から取得することを推奨）
backup_service = BackupService(
    db_path="data/recipes.db",
    backup_dir="data/backups",
    max_generations=10,
    compress=True,
)


@router.post(
    "/create", response_model=CreateBackupResponse, status_code=status.HTTP_201_CREATED
)
async def create_backup(
    request: CreateBackupRequest = CreateBackupRequest(),
) -> CreateBackupResponse:
    """
    手動バックアップを作成

    Args:
        request: バックアップ作成リクエスト

    Returns:
        CreateBackupResponse: 作成されたバックアップ情報

    Raises:
        HTTPException: バックアップ作成に失敗した場合
    """
    try:
        backup_info = backup_service.create_backup(backup_name=request.backup_name)
        return CreateBackupResponse(status="ok", data=backup_info, error=None)
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.get("/list", response_model=ListBackupsResponse)
async def list_backups() -> ListBackupsResponse:
    """
    バックアップ一覧を取得

    Returns:
        ListBackupsResponse: バックアップ情報のリスト

    Raises:
        HTTPException: 一覧取得に失敗した場合
    """
    try:
        backups = backup_service.list_backups()
        return ListBackupsResponse(status="ok", data=backups, error=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list backups: {str(e)}",
        )


@router.post("/restore/{backup_id}", response_model=RestoreBackupResponse)
async def restore_backup(backup_id: str) -> RestoreBackupResponse:
    """
    バックアップからリストアを実行

    Args:
        backup_id: リストアするバックアップのID（ファイル名）

    Returns:
        RestoreBackupResponse: リストア結果

    Raises:
        HTTPException: リストアに失敗した場合
    """
    try:
        success = backup_service.restore_backup(backup_id)
        return RestoreBackupResponse(
            status="ok",
            data={
                "backup_id": backup_id,
                "restored": success,
                "message": "Restore completed successfully",
            },
            error=None,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except IOError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}",
        )


@router.delete("/{backup_id}", response_model=DeleteBackupResponse)
async def delete_backup(backup_id: str) -> DeleteBackupResponse:
    """
    バックアップを削除

    Args:
        backup_id: 削除するバックアップのID（ファイル名）

    Returns:
        DeleteBackupResponse: 削除結果

    Raises:
        HTTPException: 削除に失敗した場合
    """
    try:
        success = backup_service.delete_backup(backup_id)
        return DeleteBackupResponse(
            status="ok",
            data={
                "backup_id": backup_id,
                "deleted": success,
                "message": "Backup deleted successfully",
            },
            error=None,
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete backup: {str(e)}",
        )


@router.get("/status", response_model=StatusResponse)
async def get_status() -> StatusResponse:
    """
    バックアップ状態を確認

    Returns:
        StatusResponse: バックアップの状態情報

    Raises:
        HTTPException: 状態取得に失敗した場合
    """
    try:
        backup_status = backup_service.get_status()
        return StatusResponse(status="ok", data=backup_status, error=None)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get status: {str(e)}",
        )
