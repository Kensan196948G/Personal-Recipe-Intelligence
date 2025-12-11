"""
YouTube字幕（トランスクリプト）からレシピ構造を解析するモジュール
"""

import re
import logging
from typing import List, Dict, Any, Optional

from .models import TimestampedStep

logger = logging.getLogger(__name__)


class TranscriptParser:
    """トランスクリプトからレシピ情報を抽出・解析"""

    def __init__(self):
        """初期化"""
        # 材料を示すキーワードパターン
        self.ingredient_patterns = [
            r"(?:材料|ざいりょう|ingredient)",
            r"(?:用意|ようい|prepare|need)",
            r"(?:\d+(?:グラム|g|ｇ|ml|大さじ|小さじ|カップ|個|本|枚))",
        ]

        # 手順を示すキーワードパターン
        self.step_patterns = [
            r"(?:まず|最初|first|start)",
            r"(?:次|つぎ|next|then)",
            r"(?:最後|finally|last)",
            r"(?:〜します|〜してください|〜ましょう)",
            r"(?:切り|刻み|炒め|煮|焼き|混ぜ|加え)",
        ]

        # 分量パターン
        self.servings_patterns = [
            r"(\d+)(?:人分|にんぶん|serving)",
            r"(?:分量|ぶんりょう)[:：]\s*(\d+)(?:人|名)",
        ]

        # 調理時間パターン
        self.time_patterns = [
            r"(?:調理時間|ちょうりじかん|cooking time)[:：]\s*(\d+)(?:分|ぷん|min|minute)",
            r"(\d+)(?:分|ぷん|min|minute)(?:で|くらい|ほど|程度)",
        ]

    def parse_recipe(
        self, transcript_text: str, transcript_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        トランスクリプトからレシピ情報を解析

        Args:
            transcript_text: 結合されたトランスクリプトテキスト
            transcript_data: タイムスタンプ付きトランスクリプトデータ

        Returns:
            解析されたレシピ情報
        """
        result = {
            "ingredients": [],
            "steps": [],
            "servings": None,
            "cooking_time": None,
        }

        try:
            # 材料抽出
            result["ingredients"] = self.extract_ingredients(transcript_text)

            # 手順抽出（タイムスタンプ付き）
            result["steps"] = self.extract_steps(transcript_data)

            # 分量抽出
            result["servings"] = self.extract_servings(transcript_text)

            # 調理時間抽出
            result["cooking_time"] = self.extract_cooking_time(transcript_text)

            logger.info(
                f"Parsed recipe: {len(result['ingredients'])} ingredients, "
                f"{len(result['steps'])} steps"
            )

        except Exception as e:
            logger.error(f"Failed to parse recipe from transcript: {e}", exc_info=True)

        return result

    def extract_ingredients(self, text: str) -> List[str]:
        """
        テキストから材料リストを抽出

        Args:
            text: トランスクリプトテキスト

        Returns:
            材料リスト
        """
        ingredients = []

        # 数値＋単位パターンで材料候補を抽出
        quantity_pattern = r"([^\s]+?)\s*(\d+(?:\.\d+)?)\s*(グラム|g|ｇ|ml|大さじ|小さじ|カップ|個|本|枚|cc|L)"

        matches = re.finditer(quantity_pattern, text, re.IGNORECASE)

        for match in matches:
            ingredient_name = match.group(1).strip()
            quantity = match.group(2)
            unit = match.group(3)

            # ノイズフィルタリング（数字のみ、記号のみを除外）
            if ingredient_name and not re.match(r"^[\d\W]+$", ingredient_name):
                ingredient = f"{ingredient_name} {quantity}{unit}"
                ingredients.append(ingredient)

        # 重複削除
        ingredients = list(dict.fromkeys(ingredients))

        return ingredients[:20]  # 最大20件に制限

    def extract_steps(
        self, transcript_data: List[Dict[str, Any]]
    ) -> List[TimestampedStep]:
        """
        トランスクリプトから手順を抽出（タイムスタンプ付き）

        Args:
            transcript_data: タイムスタンプ付きトランスクリプトデータ

        Returns:
            タイムスタンプ付き手順リスト
        """
        steps = []
        step_number = 1

        # テキストを文単位で分割して手順候補を検出
        current_step = ""
        current_timestamp = None

        for i, item in enumerate(transcript_data):
            text = item["text"].strip()
            timestamp = item.get("start", 0)

            # 手順キーワードを含むか判定
            is_step = any(
                re.search(pattern, text, re.IGNORECASE)
                for pattern in self.step_patterns
            )

            if is_step:
                # 前の手順を保存
                if current_step:
                    steps.append(
                        TimestampedStep(
                            step_number=step_number,
                            description=current_step.strip(),
                            timestamp=self._format_timestamp(current_timestamp),
                            timestamp_seconds=int(current_timestamp),
                        )
                    )
                    step_number += 1

                # 新しい手順を開始
                current_step = text
                current_timestamp = timestamp
            else:
                # 既存の手順に追加
                if current_step:
                    current_step += " " + text

        # 最後の手順を保存
        if current_step:
            steps.append(
                TimestampedStep(
                    step_number=step_number,
                    description=current_step.strip(),
                    timestamp=self._format_timestamp(current_timestamp),
                    timestamp_seconds=(
                        int(current_timestamp) if current_timestamp else None
                    ),
                )
            )

        # 手順が検出されなかった場合、時間区切りで分割
        if not steps:
            steps = self._extract_steps_by_time_segments(transcript_data)

        return steps[:30]  # 最大30件に制限

    def _extract_steps_by_time_segments(
        self, transcript_data: List[Dict[str, Any]], segment_duration: int = 30
    ) -> List[TimestampedStep]:
        """
        時間区切りで手順を抽出（フォールバック用）

        Args:
            transcript_data: トランスクリプトデータ
            segment_duration: 区切り時間（秒）

        Returns:
            タイムスタンプ付き手順リスト
        """
        steps = []
        step_number = 1
        current_segment = []
        segment_start = 0

        for item in transcript_data:
            timestamp = item.get("start", 0)
            text = item["text"].strip()

            # 区切り時間を超えたら新しい手順を作成
            if timestamp - segment_start >= segment_duration and current_segment:
                combined_text = " ".join(current_segment)

                if len(combined_text) > 10:  # 最小文字数フィルタ
                    steps.append(
                        TimestampedStep(
                            step_number=step_number,
                            description=combined_text,
                            timestamp=self._format_timestamp(segment_start),
                            timestamp_seconds=int(segment_start),
                        )
                    )
                    step_number += 1

                current_segment = []
                segment_start = timestamp

            current_segment.append(text)

        # 最後のセグメント
        if current_segment:
            combined_text = " ".join(current_segment)
            if len(combined_text) > 10:
                steps.append(
                    TimestampedStep(
                        step_number=step_number,
                        description=combined_text,
                        timestamp=self._format_timestamp(segment_start),
                        timestamp_seconds=int(segment_start),
                    )
                )

        return steps

    def extract_servings(self, text: str) -> Optional[str]:
        """
        テキストから分量・人数を抽出

        Args:
            text: トランスクリプトテキスト

        Returns:
            分量・人数、見つからない場合はNone
        """
        for pattern in self.servings_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                servings = match.group(1)
                return f"{servings}人分"

        return None

    def extract_cooking_time(self, text: str) -> Optional[str]:
        """
        テキストから調理時間を抽出

        Args:
            text: トランスクリプトテキスト

        Returns:
            調理時間、見つからない場合はNone
        """
        for pattern in self.time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                time_minutes = match.group(1)
                return f"{time_minutes}分"

        return None

    def _format_timestamp(self, seconds: Optional[float]) -> str:
        """
        秒数をMM:SS形式にフォーマット

        Args:
            seconds: 秒数

        Returns:
            MM:SS形式のタイムスタンプ
        """
        if seconds is None:
            return "00:00"

        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
