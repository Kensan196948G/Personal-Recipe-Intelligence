"""
Personal Recipe Intelligence - Common Utilities

共通ユーティリティ関数。
コード重複を削減するための共有機能。
"""

import json
import logging
from pathlib import Path
from typing import Any, Optional, TypeVar, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)

T = TypeVar("T")


def ensure_directory(path: Path) -> Path:
    """
    ディレクトリを確認・作成

    Args:
        path: ディレクトリパス

    Returns:
        作成されたディレクトリパス
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def load_json_file(
    file_path: Path,
    default: Optional[T] = None,
    create_if_missing: bool = True
) -> T:
    """
    JSONファイルを読み込み

    Args:
        file_path: ファイルパス
        default: ファイルが存在しない場合のデフォルト値
        create_if_missing: ファイルが存在しない場合に作成するか

    Returns:
        読み込んだデータ、またはデフォルト値
    """
    if default is None:
        default = {}

    try:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            if create_if_missing:
                ensure_directory(file_path.parent)
                save_json_file(file_path, default)
            return default
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in {file_path}: {e}")
        return default
    except Exception as e:
        logger.error(f"Error loading JSON file {file_path}: {e}")
        return default


def save_json_file(
    file_path: Path,
    data: Any,
    ensure_ascii: bool = False,
    indent: int = 2
) -> bool:
    """
    JSONファイルに保存

    Args:
        file_path: ファイルパス
        data: 保存するデータ
        ensure_ascii: ASCIIエンコードを強制するか
        indent: インデント幅

    Returns:
        成功した場合 True
    """
    try:
        ensure_directory(file_path.parent)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=ensure_ascii, indent=indent, default=str)
        return True
    except Exception as e:
        logger.error(f"Error saving JSON file {file_path}: {e}")
        return False


def get_iso_timestamp() -> str:
    """
    ISO8601形式のタイムスタンプを取得

    Returns:
        ISO8601形式の現在時刻
    """
    return datetime.now().isoformat()


def safe_get(data: Dict, *keys: str, default: Any = None) -> Any:
    """
    ネストされた辞書から安全に値を取得

    Args:
        data: 辞書
        *keys: キーのパス
        default: デフォルト値

    Returns:
        取得した値、またはデフォルト値
    """
    result = data
    for key in keys:
        if isinstance(result, dict):
            result = result.get(key, default)
        else:
            return default
    return result


def chunk_list(lst: List[T], chunk_size: int) -> List[List[T]]:
    """
    リストを指定サイズのチャンクに分割

    Args:
        lst: 分割するリスト
        chunk_size: チャンクサイズ

    Returns:
        チャンクのリスト
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def truncate_string(s: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    文字列を指定長で切り詰め

    Args:
        s: 対象文字列
        max_length: 最大長
        suffix: 切り詰め時のサフィックス

    Returns:
        切り詰められた文字列
    """
    if len(s) <= max_length:
        return s
    return s[:max_length - len(suffix)] + suffix
