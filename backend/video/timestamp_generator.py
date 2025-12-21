"""
タイムスタンプ付き調理手順生成モジュール

動画トランスクリプトから調理手順とタイムスタンプを抽出・マッピングする。
"""

import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class TimestampedStep:
    """タイムスタンプ付き手順"""

    step_number: int
    timestamp: str  # "00:00:00" 形式
    timestamp_seconds: int
    action: str  # 調理動作（切る、炒める、など）
    description: str  # 手順の詳細
    confidence: float  # 検出の信頼度 (0.0-1.0)


class TimestampGenerator:
    """タイムスタンプ付き手順生成器"""

    # 調理動作キーワード（優先度順）
    COOKING_ACTIONS = {
        "切る": ["切る", "切って", "カット", "刻む", "刻んで", "みじん切り", "千切り"],
        "炒める": ["炒める", "炒めて", "炒め", "ソテー", "焼く", "焼いて"],
        "煮る": ["煮る", "煮て", "煮込む", "煮込んで", "茹でる", "茹でて", "ゆでる"],
        "混ぜる": ["混ぜる", "混ぜて", "かき混ぜ", "和える", "和えて"],
        "加える": ["加える", "加えて", "入れる", "入れて", "投入"],
        "焼く": ["焼く", "焼いて", "グリル", "ロースト", "ベイク"],
        "揚げる": ["揚げる", "揚げて", "フライ", "油で"],
        "蒸す": ["蒸す", "蒸して", "スチーム"],
        "漬ける": ["漬ける", "漬けて", "マリネ", "浸す", "浸して"],
        "盛り付ける": ["盛り付け", "盛る", "盛って", "飾る", "トッピング"],
    }

    # タイムスタンプパターン
    TIMESTAMP_PATTERNS = [
        r"(\d{1,2}):(\d{2}):(\d{2})",  # 00:00:00
        r"(\d{1,2}):(\d{2})",  # 00:00
        r"(\d+)秒",  # 30秒
        r"(\d+)分(\d+)秒",  # 1分30秒
        r"(\d+)分",  # 1分
    ]

    def __init__(self):
        """初期化"""
        self.compiled_patterns = [
            re.compile(pattern) for pattern in self.TIMESTAMP_PATTERNS
        ]

    def extract_timestamps(self, transcript: str) -> List[Tuple[int, str]]:
        """
        トランスクリプトからタイムスタンプを抽出

        Args:
          transcript: トランスクリプトテキスト

        Returns:
          List[Tuple[int, str]]: (秒数, テキスト) のリスト
        """
        timestamps = []
        lines = transcript.split("\n")

        for line in lines:
            # タイムスタンプを検出
            timestamp_seconds = self._parse_timestamp(line)
            if timestamp_seconds is not None:
                # タイムスタンプを除いたテキストを取得
                text = self._remove_timestamp(line)
                if text.strip():
                    timestamps.append((timestamp_seconds, text.strip()))

        return timestamps

    def _parse_timestamp(self, text: str) -> Optional[int]:
        """
        テキストからタイムスタンプを解析して秒数に変換

        Args:
          text: 解析対象テキスト

        Returns:
          Optional[int]: 秒数（見つからない場合はNone）
        """
        # 00:00:00 形式
        match = re.search(r"(\d{1,2}):(\d{2}):(\d{2})", text)
        if match:
            hours, minutes, seconds = map(int, match.groups())
            return hours * 3600 + minutes * 60 + seconds

        # 00:00 形式
        match = re.search(r"(\d{1,2}):(\d{2})", text)
        if match:
            minutes, seconds = map(int, match.groups())
            return minutes * 60 + seconds

        # 1分30秒 形式
        match = re.search(r"(\d+)分(\d+)秒", text)
        if match:
            minutes, seconds = map(int, match.groups())
            return minutes * 60 + seconds

        # 1分 形式
        match = re.search(r"(\d+)分", text)
        if match:
            minutes = int(match.group(1))
            return minutes * 60

        # 30秒 形式
        match = re.search(r"(\d+)秒", text)
        if match:
            seconds = int(match.group(1))
            return seconds

        return None

    def _remove_timestamp(self, text: str) -> str:
        """
        テキストからタイムスタンプ部分を除去

        Args:
          text: 対象テキスト

        Returns:
          str: タイムスタンプを除去したテキスト
        """
        # すべてのタイムスタンプパターンを除去
        result = text
        for pattern in self.compiled_patterns:
            result = pattern.sub("", result)

        # 余分な空白を削除
        result = re.sub(r"\s+", " ", result).strip()
        return result

    def detect_cooking_action(self, text: str) -> Tuple[str, float]:
        """
        テキストから調理動作を検出

        Args:
          text: 解析対象テキスト

        Returns:
          Tuple[str, float]: (動作名, 信頼度)
        """
        text.lower()

        for action, keywords in self.COOKING_ACTIONS.items():
            for keyword in keywords:
                if keyword in text:
                    # キーワードが見つかった場合、信頼度を計算
                    # より長いキーワードほど信頼度が高い
                    confidence = min(1.0, len(keyword) / 10.0 + 0.5)
                    return action, confidence

        # 動作が検出されない場合
        return "その他", 0.3

    def generate_timestamped_steps(
        self, transcript: str, min_confidence: float = 0.5
    ) -> List[TimestampedStep]:
        """
        トランスクリプトからタイムスタンプ付き手順を生成

        Args:
          transcript: トランスクリプトテキスト
          min_confidence: 最小信頼度（この値未満の手順は除外）

        Returns:
          List[TimestampedStep]: タイムスタンプ付き手順のリスト
        """
        # タイムスタンプ抽出
        timestamps = self.extract_timestamps(transcript)

        steps = []
        step_number = 1

        for timestamp_seconds, text in timestamps:
            # 調理動作を検出
            action, confidence = self.detect_cooking_action(text)

            # 信頼度チェック
            if confidence >= min_confidence:
                # タイムスタンプを文字列形式に変換
                timestamp_str = self._seconds_to_timestamp(timestamp_seconds)

                step = TimestampedStep(
                    step_number=step_number,
                    timestamp=timestamp_str,
                    timestamp_seconds=timestamp_seconds,
                    action=action,
                    description=text,
                    confidence=confidence,
                )
                steps.append(step)
                step_number += 1

        return steps

    def _seconds_to_timestamp(self, seconds: int) -> str:
        """
        秒数をタイムスタンプ文字列に変換

        Args:
          seconds: 秒数

        Returns:
          str: "00:00:00" 形式のタイムスタンプ
        """
        td = timedelta(seconds=seconds)
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        secs = td.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"

    def merge_similar_steps(
        self, steps: List[TimestampedStep], time_threshold: int = 10
    ) -> List[TimestampedStep]:
        """
        近接するタイムスタンプの手順を統合

        Args:
          steps: タイムスタンプ付き手順のリスト
          time_threshold: 統合する時間閾値（秒）

        Returns:
          List[TimestampedStep]: 統合後の手順リスト
        """
        if not steps:
            return []

        merged = []
        current = steps[0]

        for next_step in steps[1:]:
            time_diff = next_step.timestamp_seconds - current.timestamp_seconds

            if time_diff <= time_threshold and current.action == next_step.action:
                # 統合: 説明を結合
                current.description = f"{current.description} {next_step.description}"
                current.confidence = max(current.confidence, next_step.confidence)
            else:
                # 現在の手順を確定
                merged.append(current)
                current = next_step

        # 最後の手順を追加
        merged.append(current)

        # ステップ番号を再割り当て
        for idx, step in enumerate(merged, 1):
            step.step_number = idx

        return merged

    def filter_by_action(
        self, steps: List[TimestampedStep], actions: List[str]
    ) -> List[TimestampedStep]:
        """
        特定の調理動作でフィルタリング

        Args:
          steps: タイムスタンプ付き手順のリスト
          actions: フィルタする動作名のリスト

        Returns:
          List[TimestampedStep]: フィルタ後の手順リスト
        """
        return [step for step in steps if step.action in actions]

    def to_dict(self, step: TimestampedStep) -> Dict:
        """
        TimestampedStep を辞書形式に変換

        Args:
          step: タイムスタンプ付き手順

        Returns:
          Dict: 辞書形式のデータ
        """
        return {
            "step_number": step.step_number,
            "timestamp": step.timestamp,
            "timestamp_seconds": step.timestamp_seconds,
            "action": step.action,
            "description": step.description,
            "confidence": step.confidence,
        }
