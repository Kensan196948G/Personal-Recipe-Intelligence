"""
動画レシピフォーマッターモジュール

タイムスタンプ付きレシピをJSON形式に整形し、フロントエンド表示用のデータを生成する。
"""

import json
from typing import List, Dict, Optional, Any
from datetime import datetime

from .timestamp_generator import TimestampedStep, TimestampGenerator


class RecipeFormatter:
    """レシピフォーマッター"""

    def __init__(self):
        """初期化"""
        self.timestamp_generator = TimestampGenerator()

    def format_recipe(
        self,
        video_url: str,
        title: str,
        steps: List[TimestampedStep],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        タイムスタンプ付きレシピをJSON形式に整形

        Args:
          video_url: 動画URL
          title: レシピタイトル
          steps: タイムスタンプ付き手順のリスト
          metadata: 追加メタデータ

        Returns:
          Dict[str, Any]: フォーマット済みレシピデータ
        """
        formatted = {
            "video_url": video_url,
            "title": title,
            "total_steps": len(steps),
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
            "steps": [self.timestamp_generator.to_dict(step) for step in steps],
            "summary": self._generate_summary(steps),
            "timeline": self._generate_timeline(steps),
            "actions_count": self._count_actions(steps),
        }

        return formatted

    def _generate_summary(self, steps: List[TimestampedStep]) -> Dict[str, Any]:
        """
        レシピサマリーを生成

        Args:
          steps: タイムスタンプ付き手順のリスト

        Returns:
          Dict[str, Any]: サマリー情報
        """
        if not steps:
            return {
                "total_time": "00:00:00",
                "total_time_seconds": 0,
                "step_count": 0,
                "action_types": 0,
            }

        total_time_seconds = max(step.timestamp_seconds for step in steps)
        total_time = self.timestamp_generator._seconds_to_timestamp(total_time_seconds)
        action_types = len(set(step.action for step in steps))

        return {
            "total_time": total_time,
            "total_time_seconds": total_time_seconds,
            "step_count": len(steps),
            "action_types": action_types,
        }

    def _generate_timeline(self, steps: List[TimestampedStep]) -> List[Dict[str, Any]]:
        """
        タイムライン形式のデータを生成

        Args:
          steps: タイムスタンプ付き手順のリスト

        Returns:
          List[Dict[str, Any]]: タイムラインデータ
        """
        timeline = []

        for step in steps:
            timeline_item = {
                "timestamp": step.timestamp,
                "timestamp_seconds": step.timestamp_seconds,
                "action": step.action,
                "description": step.description,
                "step_number": step.step_number,
            }
            timeline.append(timeline_item)

        return timeline

    def _count_actions(self, steps: List[TimestampedStep]) -> Dict[str, int]:
        """
        調理動作の出現回数をカウント

        Args:
          steps: タイムスタンプ付き手順のリスト

        Returns:
          Dict[str, int]: 動作名と出現回数のマップ
        """
        action_count = {}

        for step in steps:
            action = step.action
            action_count[action] = action_count.get(action, 0) + 1

        return action_count

    def format_for_frontend(
        self,
        video_url: str,
        title: str,
        steps: List[TimestampedStep],
        thumbnail_url: Optional[str] = None,
        description: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        フロントエンド表示用に最適化したフォーマット

        Args:
          video_url: 動画URL
          title: レシピタイトル
          steps: タイムスタンプ付き手順のリスト
          thumbnail_url: サムネイルURL
          description: レシピ説明

        Returns:
          Dict[str, Any]: フロントエンド用データ
        """
        return {
            "video": {
                "url": video_url,
                "thumbnail": thumbnail_url,
                "title": title,
                "description": description,
            },
            "recipe": {
                "steps": [
                    {
                        "id": step.step_number,
                        "time": step.timestamp,
                        "timeSeconds": step.timestamp_seconds,
                        "action": step.action,
                        "text": step.description,
                        "confidence": step.confidence,
                    }
                    for step in steps
                ],
                "totalSteps": len(steps),
                "estimatedTime": self._generate_summary(steps)["total_time"],
            },
            "navigation": {
                "chapters": self._generate_chapters(steps),
                "quickJump": self._generate_quick_jump(steps),
            },
        }

    def _generate_chapters(self, steps: List[TimestampedStep]) -> List[Dict[str, Any]]:
        """
        チャプター情報を生成（同じ動作をグループ化）

        Args:
          steps: タイムスタンプ付き手順のリスト

        Returns:
          List[Dict[str, Any]]: チャプターデータ
        """
        chapters = []
        current_action = None
        chapter_start = None
        chapter_steps = []

        for step in steps:
            if step.action != current_action:
                # 新しいチャプター開始
                if current_action is not None:
                    chapters.append(
                        {
                            "title": current_action,
                            "start": chapter_start,
                            "steps": chapter_steps,
                        }
                    )

                current_action = step.action
                chapter_start = step.timestamp
                chapter_steps = [step.step_number]
            else:
                chapter_steps.append(step.step_number)

        # 最後のチャプターを追加
        if current_action is not None:
            chapters.append(
                {
                    "title": current_action,
                    "start": chapter_start,
                    "steps": chapter_steps,
                }
            )

        return chapters

    def _generate_quick_jump(
        self, steps: List[TimestampedStep]
    ) -> List[Dict[str, Any]]:
        """
        クイックジャンプ用のポイントを生成（主要な調理動作のみ）

        Args:
          steps: タイムスタンプ付き手順のリスト

        Returns:
          List[Dict[str, Any]]: クイックジャンプデータ
        """
        # 主要な調理動作のみ抽出
        important_actions = {"切る", "炒める", "煮る", "焼く", "揚げる"}

        quick_jump = []
        seen_actions = set()

        for step in steps:
            if step.action in important_actions and step.action not in seen_actions:
                quick_jump.append(
                    {
                        "action": step.action,
                        "timestamp": step.timestamp,
                        "timestampSeconds": step.timestamp_seconds,
                        "stepNumber": step.step_number,
                    }
                )
                seen_actions.add(step.action)

        return quick_jump

    def export_to_json(
        self, data: Dict[str, Any], output_path: str, pretty: bool = True
    ) -> None:
        """
        JSONファイルにエクスポート

        Args:
          data: エクスポートするデータ
          output_path: 出力ファイルパス
          pretty: 整形して出力するか
        """
        with open(output_path, "w", encoding="utf-8") as f:
            if pretty:
                json.dump(data, f, ensure_ascii=False, indent=2)
            else:
                json.dump(data, f, ensure_ascii=False)

    def import_from_json(self, input_path: str) -> Dict[str, Any]:
        """
        JSONファイルからインポート

        Args:
          input_path: 入力ファイルパス

        Returns:
          Dict[str, Any]: インポートしたデータ
        """
        with open(input_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def format_srt_subtitles(self, steps: List[TimestampedStep]) -> str:
        """
        SRT字幕形式に変換

        Args:
          steps: タイムスタンプ付き手順のリスト

        Returns:
          str: SRT形式の字幕テキスト
        """
        srt_lines = []

        for idx, step in enumerate(steps, 1):
            # 開始時刻
            start_time = self._format_srt_timestamp(step.timestamp_seconds)

            # 終了時刻（次のステップの開始時刻 or +5秒）
            if idx < len(steps):
                end_seconds = steps[idx].timestamp_seconds
            else:
                end_seconds = step.timestamp_seconds + 5

            end_time = self._format_srt_timestamp(end_seconds)

            # SRT形式
            srt_lines.append(f"{idx}")
            srt_lines.append(f"{start_time} --> {end_time}")
            srt_lines.append(f"[{step.action}] {step.description}")
            srt_lines.append("")  # 空行

        return "\n".join(srt_lines)

    def _format_srt_timestamp(self, seconds: int) -> str:
        """
        SRT形式のタイムスタンプに変換

        Args:
          seconds: 秒数

        Returns:
          str: "00:00:00,000" 形式のタイムスタンプ
        """
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d},000"

    def generate_markdown_recipe(
        self, video_url: str, title: str, steps: List[TimestampedStep]
    ) -> str:
        """
        Markdown形式のレシピを生成

        Args:
          video_url: 動画URL
          title: レシピタイトル
          steps: タイムスタンプ付き手順のリスト

        Returns:
          str: Markdown形式のテキスト
        """
        lines = [
            f"# {title}",
            "",
            f"**動画URL**: {video_url}",
            "",
            "## 手順",
            "",
        ]

        for step in steps:
            lines.append(
                f"{step.step_number}. **[{step.timestamp}]** "
                f"*{step.action}*: {step.description}"
            )

        # サマリー
        summary = self._generate_summary(steps)
        lines.extend(
            [
                "",
                "## サマリー",
                "",
                f"- 総調理時間: {summary['total_time']}",
                f"- 手順数: {summary['step_count']}",
                f"- 調理動作種類: {summary['action_types']}",
            ]
        )

        return "\n".join(lines)
