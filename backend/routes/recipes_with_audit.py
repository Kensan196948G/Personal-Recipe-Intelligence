"""
Recipe Routes with Audit Logging Integration

監査ログ統合済みレシピAPI実装例
CLAUDE.md Section 6.4 準拠
"""

from flask import Blueprint, request, jsonify, g
from typing import Optional
from backend.services.audit_service import get_audit_service
from backend.middleware.audit_middleware import get_client_ip

# Blueprint作成（実際の実装では既存のBlueprintに統合）
recipe_bp = Blueprint("recipes", __name__, url_prefix="/api/v1/recipes")

# 監査サービス取得
audit_service = get_audit_service()


# === Helper Functions ===


def get_current_user_id() -> Optional[str]:
  """
  現在のユーザーIDを取得

  Returns:
      ユーザーID（認証済みの場合）
  """
  return getattr(g, "user_id", None)


# === Recipe CRUD Endpoints with Audit Logging ===


@recipe_bp.route("", methods=["POST"])
def create_recipe():
  """
  レシピ作成エンドポイント

  監査ログ: recipe_create
  """
  try:
    data = request.get_json()
    user_id = get_current_user_id()
    ip_address = get_client_ip(request)

    # バリデーション（実際にはPydanticを使用）
    if not data or "title" not in data:
      return jsonify({"status": "error", "error": "Title is required"}), 400

    # レシピ作成処理（実際のDB操作）
    # recipe_id = db.create_recipe(data)
    recipe_id = "recipe_123"  # 例

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


@recipe_bp.route("/<recipe_id>", methods=["PUT"])
def update_recipe(recipe_id: str):
  """
  レシピ更新エンドポイント

  監査ログ: recipe_update
  """
  try:
    data = request.get_json()
    user_id = get_current_user_id()
    ip_address = get_client_ip(request)

    # レシピ存在確認（実際のDB操作）
    # existing_recipe = db.get_recipe(recipe_id)
    # if not existing_recipe:
    #     return jsonify({"status": "error", "error": "Recipe not found"}), 404

    # 変更内容を記録
    changes = {
      "updated_fields": list(data.keys()),
      "field_count": len(data),
    }

    # レシピ更新処理
    # db.update_recipe(recipe_id, data)

    # 監査ログ記録
    audit_service.log_recipe_update(
      recipe_id=recipe_id,
      user_id=user_id,
      ip_address=ip_address,
      changes=changes,
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


@recipe_bp.route("/<recipe_id>", methods=["DELETE"])
def delete_recipe(recipe_id: str):
  """
  レシピ削除エンドポイント

  監査ログ: recipe_delete
  """
  try:
    user_id = get_current_user_id()
    ip_address = get_client_ip(request)

    # レシピ取得（タイトルを監査ログに記録するため）
    # existing_recipe = db.get_recipe(recipe_id)
    # if not existing_recipe:
    #     return jsonify({"status": "error", "error": "Recipe not found"}), 404
    # recipe_title = existing_recipe.get("title")
    recipe_title = "Example Recipe"  # 例

    # レシピ削除処理
    # db.delete_recipe(recipe_id)

    # 監査ログ記録
    audit_service.log_recipe_delete(
      recipe_id=recipe_id,
      user_id=user_id,
      ip_address=ip_address,
      recipe_title=recipe_title,
    )

    return jsonify(
      {
        "status": "ok",
        "data": {"recipe_id": recipe_id, "deleted": True},
        "error": None,
      }
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


@recipe_bp.route("/batch", methods=["DELETE"])
def batch_delete_recipes():
  """
  レシピ一括削除エンドポイント

  監査ログ: recipe_batch_delete
  """
  try:
    data = request.get_json()
    user_id = get_current_user_id()
    ip_address = get_client_ip(request)

    recipe_ids = data.get("recipe_ids", [])

    if not recipe_ids:
      return jsonify({"status": "error", "error": "No recipe IDs provided"}), 400

    # 一括削除処理
    # db.batch_delete_recipes(recipe_ids)

    # 監査ログ記録
    audit_service.log_recipe_batch_delete(
      recipe_ids=recipe_ids, user_id=user_id, ip_address=ip_address
    )

    return jsonify(
      {
        "status": "ok",
        "data": {"deleted_count": len(recipe_ids)},
        "error": None,
      }
    )

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


@recipe_bp.route("/<recipe_id>", methods=["GET"])
def get_recipe(recipe_id: str):
  """
  レシピ取得エンドポイント

  監査ログ: 読み取り操作のため通常はログ不要
  セキュリティ上重要な場合のみ記録
  """
  try:
    # レシピ取得処理
    # recipe = db.get_recipe(recipe_id)
    recipe = {"id": recipe_id, "title": "Example Recipe"}  # 例

    return jsonify({"status": "ok", "data": recipe, "error": None})

  except Exception as e:
    return jsonify({"status": "error", "error": str(e)}), 500


# === Export Blueprint ===


def register_recipe_routes(app):
  """
  レシピルートをFlaskアプリに登録

  Args:
      app: Flaskアプリケーション
  """
  app.register_blueprint(recipe_bp)
