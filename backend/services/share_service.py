"""
レシピ共有サービス

レシピを様々な形式でエクスポートし、共有リンクを生成する機能を提供する。
"""

import json
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from pathlib import Path


class ShareService:
    """レシピ共有機能を提供するサービスクラス"""

    def __init__(self, data_dir: str = "data"):
        """
        初期化

        Args:
          data_dir: データ保存ディレクトリ
        """
        self.data_dir = Path(data_dir)
        self.share_tokens_file = self.data_dir / "share_tokens.json"
        self._ensure_data_dir()

    def _ensure_data_dir(self) -> None:
        """データディレクトリが存在することを確認"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if not self.share_tokens_file.exists():
            self.share_tokens_file.write_text(json.dumps({}))

    def to_json(self, recipe: Dict[str, Any], compact: bool = True) -> str:
        """
        レシピをJSON形式に変換（共有用コンパクト版）

        Args:
          recipe: レシピデータ
          compact: コンパクト形式にするか

        Returns:
          JSON文字列
        """
        share_data = {
            "name": recipe.get("name", "無題のレシピ"),
            "description": recipe.get("description", ""),
            "servings": recipe.get("servings", 1),
            "ingredients": recipe.get("ingredients", []),
            "steps": recipe.get("steps", []),
            "tags": recipe.get("tags", []),
            "prep_time": recipe.get("prep_time"),
            "cook_time": recipe.get("cook_time"),
            "source": recipe.get("source", "Personal Recipe Intelligence"),
            "exported_at": datetime.now().isoformat(),
        }

        if compact:
            return json.dumps(share_data, ensure_ascii=False, separators=(",", ":"))
        else:
            return json.dumps(share_data, ensure_ascii=False, indent=2)

    def to_markdown(self, recipe: Dict[str, Any]) -> str:
        """
        レシピをMarkdown形式に変換（印刷・ブログ用）

        Args:
          recipe: レシピデータ

        Returns:
          Markdown文字列
        """
        name = recipe.get("name", "無題のレシピ")
        description = recipe.get("description", "")
        servings = recipe.get("servings", 1)
        ingredients = recipe.get("ingredients", [])
        steps = recipe.get("steps", [])
        tags = recipe.get("tags", [])
        prep_time = recipe.get("prep_time")
        cook_time = recipe.get("cook_time")
        source = recipe.get("source", "Personal Recipe Intelligence")

        # Markdown構築
        md_lines = [f"# {name}", ""]

        # 説明
        if description:
            md_lines.extend([description, ""])

        # タグ
        if tags:
            tag_str = " ".join([f"`{tag}`" for tag in tags])
            md_lines.extend([f"**タグ:** {tag_str}", ""])

        # 調理時間
        time_info = []
        if prep_time:
            time_info.append(f"下準備: {prep_time}分")
        if cook_time:
            time_info.append(f"調理: {cook_time}分")
        if time_info:
            md_lines.extend([f"**時間:** {' / '.join(time_info)}", ""])

        # 材料
        md_lines.extend([f"## 材料（{servings}人分）", ""])
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                item = ingredient.get("name", "")
                amount = ingredient.get("amount", "")
                unit = ingredient.get("unit", "")
                quantity = f"{amount}{unit}" if amount else ""
                md_lines.append(f"- {item}: {quantity}" if quantity else f"- {item}")
            elif isinstance(ingredient, str):
                md_lines.append(f"- {ingredient}")

        md_lines.append("")

        # 作り方
        md_lines.extend(["## 作り方", ""])
        for idx, step in enumerate(steps, 1):
            if isinstance(step, dict):
                step_text = step.get("text", step.get("description", ""))
            else:
                step_text = str(step)
            md_lines.append(f"{idx}. {step_text}")

        md_lines.extend(["", "---", f"出典: {source}"])

        return "\n".join(md_lines)

    def to_html(self, recipe: Dict[str, Any]) -> str:
        """
        レシピをHTML形式に変換（Webページ埋め込み用）

        Args:
          recipe: レシピデータ

        Returns:
          HTML文字列
        """
        name = recipe.get("name", "無題のレシピ")
        description = recipe.get("description", "")
        servings = recipe.get("servings", 1)
        ingredients = recipe.get("ingredients", [])
        steps = recipe.get("steps", [])
        tags = recipe.get("tags", [])
        prep_time = recipe.get("prep_time")
        cook_time = recipe.get("cook_time")
        source = recipe.get("source", "Personal Recipe Intelligence")

        # HTML構築
        html_parts = [
            "<!DOCTYPE html>",
            '<html lang="ja">',
            "<head>",
            '  <meta charset="UTF-8">',
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0">',
            f"  <title>{self._escape_html(name)}</title>",
            "  <style>",
            "    body { font-family: sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }",
            "    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }",
            "    h2 { color: #34495e; margin-top: 30px; }",
            "    .description { color: #555; margin: 15px 0; }",
            "    .meta { background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }",
            "    .tags { margin: 10px 0; }",
            "    .tag { display: inline-block; background: #3498db; color: white; padding: 5px 10px; ",
            "           margin: 5px 5px 5px 0; border-radius: 3px; font-size: 0.9em; }",
            "    .ingredients { list-style: none; padding: 0; }",
            "    .ingredients li { padding: 8px; border-bottom: 1px solid #ecf0f1; }",
            "    .steps { counter-reset: step-counter; list-style: none; padding: 0; }",
            "    .steps li { counter-increment: step-counter; padding: 15px; margin: 10px 0; ",
            "                background: #f8f9fa; border-left: 4px solid #3498db; position: relative; }",
            "    .steps li::before { content: counter(step-counter); position: absolute; left: -20px; ",
            "                        top: 15px; background: #3498db; color: white; width: 30px; ",
            "                        height: 30px; border-radius: 50%; display: flex; align-items: center; ",
            "                        justify-content: center; font-weight: bold; }",
            "    .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; ",
            "              color: #7f8c8d; font-size: 0.9em; text-align: center; }",
            "  </style>",
            "</head>",
            "<body>",
            f"  <h1>{self._escape_html(name)}</h1>",
        ]

        # 説明
        if description:
            html_parts.append(
                f'  <p class="description">{self._escape_html(description)}</p>'
            )

        # メタ情報
        html_parts.append('  <div class="meta">')

        # タグ
        if tags:
            html_parts.append('    <div class="tags">')
            for tag in tags:
                html_parts.append(
                    f'      <span class="tag">{self._escape_html(tag)}</span>'
                )
            html_parts.append("    </div>")

        # 時間情報
        time_info = []
        if prep_time:
            time_info.append(f"下準備: {prep_time}分")
        if cook_time:
            time_info.append(f"調理: {cook_time}分")
        if time_info:
            html_parts.append(
                f"    <p><strong>時間:</strong> {' / '.join(time_info)}</p>"
            )

        html_parts.append(f"    <p><strong>分量:</strong> {servings}人分</p>")
        html_parts.append("  </div>")

        # 材料
        html_parts.append("  <h2>材料</h2>")
        html_parts.append('  <ul class="ingredients">')
        for ingredient in ingredients:
            if isinstance(ingredient, dict):
                item = ingredient.get("name", "")
                amount = ingredient.get("amount", "")
                unit = ingredient.get("unit", "")
                quantity = f"{amount}{unit}" if amount else ""
                text = (
                    f"{self._escape_html(item)}: {self._escape_html(quantity)}"
                    if quantity
                    else self._escape_html(item)
                )
                html_parts.append(f"    <li>{text}</li>")
            elif isinstance(ingredient, str):
                html_parts.append(f"    <li>{self._escape_html(ingredient)}</li>")
        html_parts.append("  </ul>")

        # 作り方
        html_parts.append("  <h2>作り方</h2>")
        html_parts.append('  <ol class="steps">')
        for step in steps:
            if isinstance(step, dict):
                step_text = step.get("text", step.get("description", ""))
            else:
                step_text = str(step)
            html_parts.append(f"    <li>{self._escape_html(step_text)}</li>")
        html_parts.append("  </ol>")

        # フッター
        html_parts.extend(
            [
                '  <div class="footer">',
                f"    出典: {self._escape_html(source)}",
                "  </div>",
                "</body>",
                "</html>",
            ]
        )

        return "\n".join(html_parts)

    def generate_share_link(
        self, recipe_id: int, expires_hours: int = 24
    ) -> Dict[str, Any]:
        """
        共有リンク生成（一時的なトークンベース）

        Args:
          recipe_id: レシピID
          expires_hours: 有効期限（時間）

        Returns:
          トークン情報
        """
        # トークン生成
        token = secrets.token_urlsafe(32)

        # 有効期限
        expires_at = datetime.now() + timedelta(hours=expires_hours)

        # トークン情報
        token_data = {
            "recipe_id": recipe_id,
            "token": token,
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at.isoformat(),
            "access_count": 0,
        }

        # 既存のトークンを読み込み
        tokens = self._load_share_tokens()

        # トークンを保存
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        tokens[token_hash] = token_data

        self._save_share_tokens(tokens)

        return {
            "token": token,
            "expires_at": expires_at.isoformat(),
            "share_url": f"/api/v1/share/link/{token}",
        }

    def verify_share_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        共有トークンの検証

        Args:
          token: 共有トークン

        Returns:
          トークン情報（無効な場合はNone）
        """
        tokens = self._load_share_tokens()
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        token_data = tokens.get(token_hash)

        if not token_data:
            return None

        # 有効期限チェック
        expires_at = datetime.fromisoformat(token_data["expires_at"])
        if datetime.now() > expires_at:
            # 期限切れトークンを削除
            del tokens[token_hash]
            self._save_share_tokens(tokens)
            return None

        # アクセスカウント更新
        token_data["access_count"] += 1
        tokens[token_hash] = token_data
        self._save_share_tokens(tokens)

        return token_data

    def revoke_share_token(self, token: str) -> bool:
        """
        共有トークンの無効化

        Args:
          token: 共有トークン

        Returns:
          無効化成功フラグ
        """
        tokens = self._load_share_tokens()
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        if token_hash in tokens:
            del tokens[token_hash]
            self._save_share_tokens(tokens)
            return True

        return False

    def cleanup_expired_tokens(self) -> int:
        """
        期限切れトークンのクリーンアップ

        Returns:
          削除したトークン数
        """
        tokens = self._load_share_tokens()
        now = datetime.now()

        expired_tokens = [
            token_hash
            for token_hash, token_data in tokens.items()
            if datetime.fromisoformat(token_data["expires_at"]) <= now
        ]

        for token_hash in expired_tokens:
            del tokens[token_hash]

        if expired_tokens:
            self._save_share_tokens(tokens)

        return len(expired_tokens)

    def _load_share_tokens(self) -> Dict[str, Any]:
        """共有トークンを読み込み"""
        try:
            return json.loads(self.share_tokens_file.read_text())
        except (json.JSONDecodeError, FileNotFoundError):
            return {}

    def _save_share_tokens(self, tokens: Dict[str, Any]) -> None:
        """共有トークンを保存"""
        self.share_tokens_file.write_text(
            json.dumps(tokens, ensure_ascii=False, indent=2)
        )

    @staticmethod
    def _escape_html(text: str) -> str:
        """HTMLエスケープ"""
        return (
            str(text)
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#x27;")
        )
