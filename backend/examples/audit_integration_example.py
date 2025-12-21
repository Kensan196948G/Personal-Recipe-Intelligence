"""
Audit Logging Integration Example

監査ログ統合の実装例
CLAUDE.md Section 6.4 準拠
"""

from flask import Flask, request, jsonify, g
from backend.services.audit_service import get_audit_service
from backend.middleware.auth_with_audit import require_auth, optional_auth
from backend.middleware.audit_middleware import get_client_ip

# Flask アプリケーション作成
app = Flask(__name__)

# 監査サービス取得
audit_service = get_audit_service()


# === 例1: レシピ作成エンドポイント（監査ログ統合） ===


@app.route("/api/v1/recipes", methods=["POST"])
@require_auth  # 認証必須（自動的に認証ログ記録）
def create_recipe():
  """
  レシピ作成エンドポイント

  監査ログ:
  - 認証成功/失敗（@require_auth デコレータが自動記録）
  - レシピ作成（手動記録）
  """
  try:
    data = request.get_json()
    user_id = g.user_id
    ip_address = get_client_ip(request)

    # バリデーション
    if not data or "title" not in data:
      return jsonify({"status": "error", "error": "Title is required"}), 400

    # レシピ作成処理（実際のDB操作）
    recipe_id = f"recipe_{data['title'].replace(' ', '_').lower()}"

    # 監査ログ記録
    audit_service.log_recipe_create(
      recipe_id=recipe_id,
      user_id=user_id,
      ip_address=ip_address,
      recipe_title=data.get("title"),
    )

    return (
      jsonify(
        {
          "status": "ok",
          "data": {"recipe_id": recipe_id, "title": data.get("title")},
          "error": None,
        }
      ),
      201,
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === 例2: レシピ更新エンドポイント（詳細な変更記録） ===


@app.route("/api/v1/recipes/<recipe_id>", methods=["PUT"])
@require_auth
def update_recipe(recipe_id: str):
  """
  レシピ更新エンドポイント

  監査ログ: 変更内容の詳細を記録
  """
  try:
    data = request.get_json()
    user_id = g.user_id
    ip_address = get_client_ip(request)

    # 既存レシピの取得（実際のDB操作）
    existing_recipe = {"title": "Old Title", "ingredients": ["材料1", "材料2"]}

    # 変更内容を詳細に記録
    changes = {
      "updated_fields": list(data.keys()),
      "field_count": len(data),
      "before": {},
      "after": {},
    }

    # 各フィールドの変更前後を記録
    for field in data.keys():
      if field in existing_recipe:
        changes["before"][field] = existing_recipe[field]
        changes["after"][field] = data[field]

    # レシピ更新処理
    # db.update_recipe(recipe_id, data)

    # 監査ログ記録
    audit_service.log_recipe_update(
      recipe_id=recipe_id, user_id=user_id, ip_address=ip_address, changes=changes
    )

    return jsonify(
      {
        "status": "ok",
        "data": {"recipe_id": recipe_id, "updated": True},
        "error": None,
      }
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === 例3: 管理者用設定変更エンドポイント ===


@app.route("/api/v1/admin/config", methods=["PUT"])
@require_auth
def update_config():
  """
  管理者用設定変更エンドポイント

  監査ログ: 設定変更の詳細を記録
  """
  try:
    data = request.get_json()
    user_id = g.user_id
    ip_address = get_client_ip(request)

    # 管理者権限チェック（実際の実装）
    # if not is_admin(user_id):
    #     return jsonify({"status": "error", "error": "Forbidden"}), 403

    config_key = data.get("key")
    new_value = data.get("value")

    # 既存の設定値を取得
    old_value = "old_setting_value"  # 実際のDB操作

    # 設定更新処理
    # db.update_config(config_key, new_value)

    # 監査ログ記録
    audit_service.log_admin_config_updated(
      user_id=user_id,
      config_key=config_key,
      ip_address=ip_address,
      old_value=old_value,
      new_value=new_value,
    )

    return jsonify(
      {
        "status": "ok",
        "data": {"config_key": config_key, "value": new_value},
        "error": None,
      }
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === 例4: データエクスポートエンドポイント ===


@app.route("/api/v1/export", methods=["POST"])
@require_auth
def export_data():
  """
  データエクスポートエンドポイント

  監査ログ: エクスポート操作を記録
  """
  try:
    data = request.get_json()
    user_id = g.user_id
    ip_address = get_client_ip(request)

    export_format = data.get("format", "json")

    # データエクスポート処理
    # exported_data = db.export_all_recipes(format=export_format)
    record_count = 100  # 例

    # 監査ログ記録
    audit_service.log_data_export(
      user_id=user_id,
      ip_address=ip_address,
      record_count=record_count,
      format=export_format,
    )

    return jsonify(
      {
        "status": "ok",
        "data": {"record_count": record_count, "format": export_format},
        "error": None,
      }
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === 例5: セキュリティイベントの記録 ===


@app.before_request
def security_check():
  """
  リクエスト前のセキュリティチェック

  不審なアクセスを検出して監査ログに記録
  """
  ip_address = get_client_ip(request)

  # SQLインジェクション試行の検出
  suspicious_patterns = ["' OR 1=1", "'; DROP TABLE", "<script>", "UNION SELECT"]

  for key, value in request.args.items():
    for pattern in suspicious_patterns:
      if pattern.lower() in str(value).lower():
        # セキュリティ侵害試行を記録
        audit_service.log_security_breach_attempt(
          ip_address=ip_address,
          attack_type="sql_injection",
          details={"endpoint": request.path, "parameter": key, "value": value},
        )
        return jsonify({"status": "error", "error": "Forbidden"}), 403


# === 例6: カスタム監査ログ記録 ===


@app.route("/api/v1/recipes/<recipe_id>/share", methods=["POST"])
@require_auth
def share_recipe(recipe_id: str):
  """
  レシピ共有エンドポイント

  カスタム監査ログ: 汎用logメソッドを使用
  """
  try:
    from backend.services.audit_service import AuditAction, AuditResourceType

    data = request.get_json()
    user_id = g.user_id
    ip_address = get_client_ip(request)

    share_method = data.get("method", "link")  # link, email, etc.

    # レシピ共有処理
    # ...

    # カスタム監査ログ記録（既存のメソッドがない場合）
    audit_service.log(
      action=AuditAction.RECIPE_READ,  # 既存のActionを使用
      resource_type=AuditResourceType.RECIPE,
      user_id=user_id,
      resource_id=recipe_id,
      ip_address=ip_address,
      details={"action_type": "share", "share_method": share_method},
      status="success",
    )

    return jsonify({"status": "ok", "data": {"shared": True}, "error": None})

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === 例7: エラー時の監査ログ記録 ===


@app.errorhandler(500)
def internal_error(error):
  """
  内部エラーハンドラ

  エラーも監査ログに記録
  """
  user_id = getattr(g, "user_id", None)
  ip_address = get_client_ip(request)

  # エラーを監査ログに記録
  audit_service.log(
    action=AuditAction.SECURITY_BREACH_ATTEMPT,
    resource_type=AuditResourceType.SYSTEM,
    user_id=user_id,
    ip_address=ip_address,
    details={"error": str(error), "endpoint": request.path},
    status="failure",
  )

  return jsonify({"status": "error", "error": "Internal server error"}), 500


# === 例8: バックアップ作成 ===


@app.route("/api/v1/admin/backup", methods=["POST"])
@require_auth
def create_backup():
  """
  バックアップ作成エンドポイント

  監査ログ: バックアップ作成を記録
  """
  try:
    user_id = g.user_id
    ip_address = get_client_ip(request)

    # 管理者権限チェック
    # if not is_admin(user_id):
    #     return jsonify({"status": "error", "error": "Forbidden"}), 403

    # バックアップ作成処理
    import time

    backup_id = f"backup_{int(time.time())}"
    backup_size = 1024000  # 例: 1MB

    # 監査ログ記録
    audit_service.log_admin_backup_created(
      user_id=user_id,
      backup_id=backup_id,
      ip_address=ip_address,
      backup_size=backup_size,
    )

    return jsonify(
      {
        "status": "ok",
        "data": {"backup_id": backup_id, "size": backup_size},
        "error": None,
      }
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === 実行例 ===

if __name__ == "__main__":
  print("Audit Logging Integration Example")
  print("=" * 50)
  print()
  print("利用可能なエンドポイント:")
  print("  POST   /api/v1/recipes              - レシピ作成")
  print("  PUT    /api/v1/recipes/<id>         - レシピ更新")
  print("  PUT    /api/v1/admin/config         - 設定変更")
  print("  POST   /api/v1/export               - データエクスポート")
  print("  POST   /api/v1/recipes/<id>/share   - レシピ共有")
  print("  POST   /api/v1/admin/backup         - バックアップ作成")
  print()
  print("すべてのエンドポイントで監査ログが自動記録されます。")
  print()
  print("テスト実行:")
  print("  flask run --host=0.0.0.0 --port=5000")
  print()

  # 開発サーバー起動
  # app.run(debug=True, host="0.0.0.0", port=5000)
