"""
管理者サービス

利用統計の集計、システム設定管理、ログ分析、パフォーマンス監視を提供。
JSONファイルベースの永続化を使用。
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class AdminService:
  """管理者機能を提供するサービスクラス"""

  def __init__(self, data_dir: str = "data"):
    self.data_dir = Path(data_dir)
    self.settings_file = self.data_dir / "settings.json"
    self.stats_cache_file = self.data_dir / "stats_cache.json"
    self.recipes_file = self.data_dir / "recipes.json"
    self.users_file = self.data_dir / "users.json"
    self.cache_ttl = 300  # 5分
    self._ensure_data_dir()

  def _ensure_data_dir(self) -> None:
    """データディレクトリの存在を確認"""
    self.data_dir.mkdir(parents=True, exist_ok=True)

  def _load_recipes(self) -> List[Dict[str, Any]]:
    """レシピデータを読み込み"""
    if self.recipes_file.exists():
      with open(self.recipes_file, "r", encoding="utf-8") as f:
        return json.load(f)
    return []

  def _load_users(self) -> List[Dict[str, Any]]:
    """ユーザーデータを読み込み"""
    if self.users_file.exists():
      with open(self.users_file, "r", encoding="utf-8") as f:
        return json.load(f)
    return []

  def get_system_stats(self) -> Dict[str, Any]:
    """
    システム全体の統計情報を取得

    Returns:
      Dict[str, Any]: システム統計
    """
    # キャッシュチェック
    cached = self._get_cached_stats()
    if cached:
      return cached

    recipes = self._load_recipes()
    users = self._load_users()

    # レシピ統計
    total_recipes = len(recipes)
    public_recipes = sum(1 for r in recipes if r.get("is_public", False))
    private_recipes = total_recipes - public_recipes

    # ユーザー統計
    total_users = len(users)
    now = datetime.utcnow()
    thirty_days_ago = (now - timedelta(days=30)).isoformat()
    active_users = sum(
      1 for u in users
      if u.get("last_login_at", "") >= thirty_days_ago
    )

    # 最近の活動
    week_ago = (now - timedelta(days=7)).isoformat()
    recent_recipes = sum(
      1 for r in recipes
      if r.get("created_at", "") >= week_ago
    )

    # タグ統計
    tag_counts: Dict[str, int] = {}
    for recipe in recipes:
      for tag in recipe.get("tags", []):
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]

    stats = {
      "timestamp": now.isoformat(),
      "recipes": {
        "total": total_recipes,
        "public": public_recipes,
        "private": private_recipes,
        "recent_week": recent_recipes,
      },
      "users": {
        "total": total_users,
        "active_30d": active_users,
      },
      "tags": {
        "total": len(tag_counts),
        "top": [{"name": tag, "count": count} for tag, count in top_tags],
      },
      "system": {
        "uptime": self._get_uptime(),
        "database_size": self._get_database_size(),
        "storage_used": self._get_storage_used(),
      },
    }

    # キャッシュ保存
    self._save_stats_cache(stats)

    return stats

  def get_recipe_stats(self, days: int = 30) -> Dict[str, Any]:
    """
    レシピ統計を取得

    Args:
      days: 集計対象期間（日数）

    Returns:
      Dict[str, Any]: レシピ統計
    """
    recipes = self._load_recipes()
    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    # 期間内のレシピをフィルタ
    period_recipes = [
      r for r in recipes
      if r.get("created_at", "") >= start_date
    ]

    # 日別レシピ作成数
    daily_counts: Dict[str, int] = {}
    for recipe in period_recipes:
      created_at = recipe.get("created_at", "")
      if created_at:
        date_key = created_at[:10]  # YYYY-MM-DD
        daily_counts[date_key] = daily_counts.get(date_key, 0) + 1

    # ソースごとの統計
    source_counts: Dict[str, int] = {}
    for recipe in period_recipes:
      source_url = recipe.get("source_url")
      if source_url:
        from urllib.parse import urlparse
        domain = urlparse(source_url).netloc
        source_counts[domain] = source_counts.get(domain, 0) + 1
      else:
        source_counts["manual"] = source_counts.get("manual", 0) + 1

    # 平均調理時間
    cooking_times = [
      r.get("cooking_time", 0)
      for r in period_recipes
      if r.get("cooking_time", 0) > 0
    ]
    avg_cooking_time = (
      sum(cooking_times) / len(cooking_times) if cooking_times else 0
    )

    # 平均人数
    servings = [
      r.get("servings", 0)
      for r in period_recipes
      if r.get("servings", 0) > 0
    ]
    avg_servings = sum(servings) / len(servings) if servings else 0

    return {
      "period_days": days,
      "total_recipes": len(period_recipes),
      "daily_counts": [
        {"date": date, "count": count}
        for date, count in sorted(daily_counts.items())
      ],
      "source_counts": [
        {"source": source, "count": count}
        for source, count in sorted(
          source_counts.items(), key=lambda x: x[1], reverse=True
        )
      ],
      "averages": {
        "cooking_time": round(avg_cooking_time, 1),
        "servings": round(avg_servings, 1),
      },
    }

  def get_user_stats(self, days: int = 30) -> Dict[str, Any]:
    """
    ユーザー統計を取得

    Args:
      days: 集計対象期間（日数）

    Returns:
      Dict[str, Any]: ユーザー統計
    """
    users = self._load_users()
    recipes = self._load_recipes()
    start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()

    # 日別ログイン数
    daily_logins: Dict[str, int] = {}
    active_users_list = []
    for user in users:
      last_login = user.get("last_login_at", "")
      if last_login >= start_date:
        date_key = last_login[:10]
        daily_logins[date_key] = daily_logins.get(date_key, 0) + 1
        active_users_list.append(user)

    # 新規ユーザー
    new_users = sum(
      1 for u in users
      if u.get("created_at", "") >= start_date
    )

    # アクティブユーザー（レシピ作成数でランキング）
    user_recipe_counts = []
    for user in users:
      user_id = user.get("id")
      recipe_count = sum(
        1 for r in recipes
        if r.get("user_id") == user_id
      )
      if recipe_count > 0:
        user_recipe_counts.append({
          "username": user.get("username", ""),
          "email": user.get("email", ""),
          "recipe_count": recipe_count,
        })

    user_recipe_counts.sort(key=lambda x: x["recipe_count"], reverse=True)

    return {
      "period_days": days,
      "new_users": new_users,
      "active_users": len(active_users_list),
      "daily_logins": [
        {"date": date, "count": count}
        for date, count in sorted(daily_logins.items())
      ],
      "top_contributors": user_recipe_counts[:10],
    }

  def get_settings(self) -> Dict[str, Any]:
    """
    システム設定を取得

    Returns:
      Dict[str, Any]: システム設定
    """
    if self.settings_file.exists():
      with open(self.settings_file, "r", encoding="utf-8") as f:
        return json.load(f)

    # デフォルト設定
    default_settings = {
      "site_name": "Personal Recipe Intelligence",
      "max_upload_size_mb": 10,
      "enable_public_recipes": True,
      "enable_user_registration": True,
      "default_language": "ja",
      "timezone": "Asia/Tokyo",
      "pagination_size": 20,
      "cache_ttl_seconds": 300,
      "ocr_enabled": True,
      "scraping_enabled": True,
      "max_recipes_per_user": 1000,
      "maintenance_mode": False,
    }

    self._save_settings(default_settings)
    return default_settings

  def update_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
    """
    システム設定を更新

    Args:
      settings: 更新する設定

    Returns:
      Dict[str, Any]: 更新後の設定
    """
    current_settings = self.get_settings()
    current_settings.update(settings)
    self._save_settings(current_settings)
    return current_settings

  def get_system_logs(
    self, limit: int = 100, level: Optional[str] = None
  ) -> List[Dict[str, Any]]:
    """
    システムログを取得

    Args:
      limit: 取得件数
      level: ログレベルフィルタ (ERROR, WARNING, INFO)

    Returns:
      List[Dict[str, Any]]: ログエントリー
    """
    logs_dir = Path("logs")
    if not logs_dir.exists():
      return []

    log_entries: List[Dict[str, Any]] = []

    # 最新のログファイルを読み込み
    log_files = sorted(logs_dir.glob("*.log"), key=os.path.getmtime, reverse=True)

    for log_file in log_files[:5]:  # 最新5ファイル
      try:
        with open(log_file, "r", encoding="utf-8") as f:
          for line in f:
            line = line.strip()
            if not line:
              continue

            # JSON形式のログをパース
            try:
              entry = json.loads(line)
              if level and entry.get("level") != level:
                continue
              log_entries.append(entry)
            except json.JSONDecodeError:
              # テキスト形式のログ
              log_entries.append({
                "timestamp": datetime.utcnow().isoformat(),
                "level": "INFO",
                "message": line,
              })

            if len(log_entries) >= limit:
              break

        if len(log_entries) >= limit:
          break

      except Exception as e:
        print(f"Error reading log file {log_file}: {e}")
        continue

    return log_entries[:limit]

  def get_health_check(self) -> Dict[str, Any]:
    """
    システムヘルスチェックを実行

    Returns:
      Dict[str, Any]: ヘルスチェック結果
    """
    health = {
      "status": "healthy",
      "timestamp": datetime.utcnow().isoformat(),
      "checks": {},
    }

    # データベース（JSONファイル）チェック
    try:
      if self.data_dir.exists() and os.access(self.data_dir, os.W_OK):
        health["checks"]["database"] = {"status": "ok", "message": "Data directory accessible"}
      else:
        health["checks"]["database"] = {"status": "error", "message": "Data directory not accessible"}
        health["status"] = "unhealthy"
    except Exception as e:
      health["checks"]["database"] = {"status": "error", "message": str(e)}
      health["status"] = "unhealthy"

    # ディスク容量チェック
    try:
      import shutil
      total, used, free = shutil.disk_usage("/")
      usage_percent = (used / total) * 100

      health["checks"]["disk"] = {
        "status": "ok" if usage_percent < 90 else "warning",
        "usage_percent": round(usage_percent, 2),
        "free_gb": round(free / (1024**3), 2),
      }

      if usage_percent >= 90:
        health["status"] = "degraded"

    except Exception as e:
      health["checks"]["disk"] = {"status": "error", "message": str(e)}

    # メモリチェック
    try:
      import psutil
      memory = psutil.virtual_memory()
      health["checks"]["memory"] = {
        "status": "ok" if memory.percent < 90 else "warning",
        "usage_percent": memory.percent,
        "available_gb": round(memory.available / (1024**3), 2),
      }

      if memory.percent >= 90:
        health["status"] = "degraded"

    except ImportError:
      health["checks"]["memory"] = {
        "status": "unknown",
        "message": "psutil not installed",
      }
    except Exception as e:
      health["checks"]["memory"] = {"status": "error", "message": str(e)}

    # データディレクトリチェック
    try:
      if self.data_dir.exists() and os.access(self.data_dir, os.W_OK):
        health["checks"]["data_directory"] = {
          "status": "ok",
          "message": "Writable",
        }
      else:
        health["checks"]["data_directory"] = {
          "status": "error",
          "message": "Not writable",
        }
        health["status"] = "unhealthy"
    except Exception as e:
      health["checks"]["data_directory"] = {"status": "error", "message": str(e)}
      health["status"] = "unhealthy"

    return health

  def _get_cached_stats(self) -> Optional[Dict[str, Any]]:
    """キャッシュされた統計を取得"""
    if not self.stats_cache_file.exists():
      return None

    try:
      with open(self.stats_cache_file, "r", encoding="utf-8") as f:
        cache = json.load(f)

      # キャッシュの有効期限チェック
      timestamp = datetime.fromisoformat(cache["timestamp"])
      if (datetime.utcnow() - timestamp).total_seconds() > self.cache_ttl:
        return None

      return cache

    except Exception:
      return None

  def _save_stats_cache(self, stats: Dict[str, Any]) -> None:
    """統計をキャッシュに保存"""
    try:
      with open(self.stats_cache_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    except Exception as e:
      print(f"Failed to save stats cache: {e}")

  def _save_settings(self, settings: Dict[str, Any]) -> None:
    """設定をファイルに保存"""
    with open(self.settings_file, "w", encoding="utf-8") as f:
      json.dump(settings, f, ensure_ascii=False, indent=2)

  def _get_uptime(self) -> str:
    """システムアップタイムを取得"""
    try:
      with open("/proc/uptime", "r") as f:
        uptime_seconds = float(f.readline().split()[0])
      days = int(uptime_seconds // 86400)
      hours = int((uptime_seconds % 86400) // 3600)
      minutes = int((uptime_seconds % 3600) // 60)
      return f"{days}d {hours}h {minutes}m"
    except Exception:
      return "unknown"

  def _get_database_size(self) -> str:
    """データベースファイルサイズを取得"""
    try:
      db_path = self.recipes_file
      if db_path.exists():
        size_bytes = db_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
      return "0 MB"
    except Exception:
      return "unknown"

  def _get_storage_used(self) -> str:
    """data ディレクトリの使用容量を取得"""
    try:
      total_size = 0
      for dirpath, dirnames, filenames in os.walk(self.data_dir):
        for filename in filenames:
          filepath = os.path.join(dirpath, filename)
          total_size += os.path.getsize(filepath)
      size_mb = total_size / (1024 * 1024)
      return f"{size_mb:.2f} MB"
    except Exception:
      return "unknown"

  def clear_stats_cache(self) -> None:
    """統計キャッシュをクリア"""
    if self.stats_cache_file.exists():
      self.stats_cache_file.unlink()
