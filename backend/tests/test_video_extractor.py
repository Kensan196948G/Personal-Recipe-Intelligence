"""
動画レシピ抽出機能のユニットテスト

タイムスタンプ生成とレシピフォーマット機能をテストする。
"""

import pytest
from typing import List

from backend.video.timestamp_generator import (
    TimestampGenerator,
    TimestampedStep,
)
from backend.video.recipe_formatter import RecipeFormatter


class TestTimestampGenerator:
    """TimestampGenerator のテストクラス"""

    @pytest.fixture
    def generator(self) -> TimestampGenerator:
        """テスト用ジェネレーターを作成"""
        return TimestampGenerator()

    @pytest.fixture
    def sample_transcript(self) -> str:
        """サンプルトランスクリプト"""
        return """
00:00:15 玉ねぎを薄切りにします
00:00:45 フライパンで玉ねぎを炒めます
00:01:30 豚肉を加えて炒めます
00:02:00 醤油とみりんを加えます
00:03:15 弱火で5分煮込みます
00:04:30 お皿に盛り付けて完成です
    """

    def test_parse_timestamp_hhmmss(self, generator):
        """タイムスタンプ解析テスト: HH:MM:SS 形式"""
        assert generator._parse_timestamp("00:01:30") == 90
        assert generator._parse_timestamp("01:00:00") == 3600
        assert generator._parse_timestamp("00:00:15") == 15

    def test_parse_timestamp_mmss(self, generator):
        """タイムスタンプ解析テスト: MM:SS 形式"""
        assert generator._parse_timestamp("01:30") == 90
        assert generator._parse_timestamp("10:00") == 600
        assert generator._parse_timestamp("00:15") == 15

    def test_parse_timestamp_japanese(self, generator):
        """タイムスタンプ解析テスト: 日本語形式"""
        assert generator._parse_timestamp("1分30秒") == 90
        assert generator._parse_timestamp("5分") == 300
        assert generator._parse_timestamp("30秒") == 30

    def test_parse_timestamp_none(self, generator):
        """タイムスタンプ解析テスト: タイムスタンプなし"""
        assert generator._parse_timestamp("玉ねぎを切ります") is None
        assert generator._parse_timestamp("") is None

    def test_remove_timestamp(self, generator):
        """タイムスタンプ除去テスト"""
        assert generator._remove_timestamp("00:01:30 玉ねぎを切る") == "玉ねぎを切る"
        assert generator._remove_timestamp("1分30秒 炒める") == "炒める"
        assert generator._remove_timestamp("玉ねぎを切る") == "玉ねぎを切る"

    def test_detect_cooking_action_cut(self, generator):
        """調理動作検出テスト: 切る"""
        action, confidence = generator.detect_cooking_action("玉ねぎを切ります")
        assert action == "切る"
        assert confidence > 0.5

        action, confidence = generator.detect_cooking_action("野菜を刻んでください")
        assert action == "切る"
        assert confidence > 0.5

    def test_detect_cooking_action_fry(self, generator):
        """調理動作検出テスト: 炒める"""
        action, confidence = generator.detect_cooking_action("フライパンで炒めます")
        assert action == "炒める"
        assert confidence > 0.5

    def test_detect_cooking_action_boil(self, generator):
        """調理動作検出テスト: 煮る"""
        action, confidence = generator.detect_cooking_action("弱火で煮込みます")
        assert action == "煮る"
        assert confidence > 0.5

        action, confidence = generator.detect_cooking_action("お湯で茹でます")
        assert action == "煮る"
        assert confidence > 0.5

    def test_detect_cooking_action_mix(self, generator):
        """調理動作検出テスト: 混ぜる"""
        action, confidence = generator.detect_cooking_action("よく混ぜてください")
        assert action == "混ぜる"
        assert confidence > 0.5

    def test_detect_cooking_action_add(self, generator):
        """調理動作検出テスト: 加える"""
        action, confidence = generator.detect_cooking_action("調味料を加えます")
        assert action == "加える"
        assert confidence > 0.5

    def test_detect_cooking_action_plate(self, generator):
        """調理動作検出テスト: 盛り付ける"""
        action, confidence = generator.detect_cooking_action("お皿に盛り付けます")
        assert action == "盛り付ける"
        assert confidence > 0.5

    def test_detect_cooking_action_other(self, generator):
        """調理動作検出テスト: その他"""
        action, confidence = generator.detect_cooking_action("材料を準備します")
        assert action == "その他"
        assert confidence < 0.5

    def test_extract_timestamps(self, generator, sample_transcript):
        """タイムスタンプ抽出テスト"""
        timestamps = generator.extract_timestamps(sample_transcript)

        assert len(timestamps) == 6
        assert timestamps[0] == (15, "玉ねぎを薄切りにします")
        assert timestamps[1] == (45, "フライパンで玉ねぎを炒めます")
        assert timestamps[5] == (270, "お皿に盛り付けて完成です")

    def test_generate_timestamped_steps(self, generator, sample_transcript):
        """タイムスタンプ付き手順生成テスト"""
        steps = generator.generate_timestamped_steps(sample_transcript)

        assert len(steps) > 0
        assert all(isinstance(step, TimestampedStep) for step in steps)

        # 最初の手順をチェック
        first_step = steps[0]
        assert first_step.step_number == 1
        assert first_step.timestamp == "00:00:15"
        assert first_step.timestamp_seconds == 15
        assert first_step.action == "切る"
        assert "玉ねぎ" in first_step.description
        assert first_step.confidence >= 0.5

    def test_generate_timestamped_steps_with_min_confidence(
        self, generator, sample_transcript
    ):
        """信頼度フィルタ付き手順生成テスト"""
        # 信頼度 0.8 以上のみ
        steps = generator.generate_timestamped_steps(
            sample_transcript, min_confidence=0.8
        )

        # すべての手順が信頼度 0.8 以上
        assert all(step.confidence >= 0.8 for step in steps)

    def test_seconds_to_timestamp(self, generator):
        """秒数→タイムスタンプ変換テスト"""
        assert generator._seconds_to_timestamp(15) == "00:00:15"
        assert generator._seconds_to_timestamp(90) == "00:01:30"
        assert generator._seconds_to_timestamp(3665) == "01:01:05"

    def test_merge_similar_steps(self, generator):
        """近接手順統合テスト"""
        steps = [
            TimestampedStep(1, "00:00:10", 10, "切る", "玉ねぎを切る", 0.9),
            TimestampedStep(2, "00:00:15", 15, "切る", "人参を切る", 0.9),
            TimestampedStep(3, "00:01:00", 60, "炒める", "野菜を炒める", 0.9),
        ]

        merged = generator.merge_similar_steps(steps, time_threshold=10)

        # 最初の2つが統合される
        assert len(merged) == 2
        assert merged[0].action == "切る"
        assert "玉ねぎ" in merged[0].description and "人参" in merged[0].description

    def test_filter_by_action(self, generator):
        """動作フィルタテスト"""
        steps = [
            TimestampedStep(1, "00:00:10", 10, "切る", "玉ねぎを切る", 0.9),
            TimestampedStep(2, "00:01:00", 60, "炒める", "野菜を炒める", 0.9),
            TimestampedStep(3, "00:02:00", 120, "煮る", "スープを煮る", 0.9),
        ]

        filtered = generator.filter_by_action(steps, ["切る", "炒める"])
        assert len(filtered) == 2
        assert all(step.action in ["切る", "炒める"] for step in filtered)

    def test_to_dict(self, generator):
        """辞書変換テスト"""
        step = TimestampedStep(1, "00:00:10", 10, "切る", "玉ねぎを切る", 0.9)
        result = generator.to_dict(step)

        assert result["step_number"] == 1
        assert result["timestamp"] == "00:00:10"
        assert result["timestamp_seconds"] == 10
        assert result["action"] == "切る"
        assert result["description"] == "玉ねぎを切る"
        assert result["confidence"] == 0.9


class TestRecipeFormatter:
    """RecipeFormatter のテストクラス"""

    @pytest.fixture
    def formatter(self) -> RecipeFormatter:
        """テスト用フォーマッターを作成"""
        return RecipeFormatter()

    @pytest.fixture
    def sample_steps(self) -> List[TimestampedStep]:
        """サンプル手順"""
        return [
            TimestampedStep(1, "00:00:15", 15, "切る", "玉ねぎを薄切りにします", 0.9),
            TimestampedStep(2, "00:00:45", 45, "炒める", "フライパンで炒めます", 0.9),
            TimestampedStep(3, "00:01:30", 90, "加える", "豚肉を加えます", 0.8),
            TimestampedStep(4, "00:03:15", 195, "煮る", "弱火で煮込みます", 0.9),
            TimestampedStep(
                5, "00:04:30", 270, "盛り付ける", "お皿に盛り付けます", 0.9
            ),
        ]

    def test_format_recipe(self, formatter, sample_steps):
        """レシピフォーマットテスト"""
        result = formatter.format_recipe(
            video_url="https://youtube.com/watch?v=test",
            title="テスト料理",
            steps=sample_steps,
        )

        assert result["video_url"] == "https://youtube.com/watch?v=test"
        assert result["title"] == "テスト料理"
        assert result["total_steps"] == 5
        assert "created_at" in result
        assert len(result["steps"]) == 5
        assert "summary" in result
        assert "timeline" in result
        assert "actions_count" in result

    def test_generate_summary(self, formatter, sample_steps):
        """サマリー生成テスト"""
        summary = formatter._generate_summary(sample_steps)

        assert summary["total_time"] == "00:04:30"
        assert summary["total_time_seconds"] == 270
        assert summary["step_count"] == 5
        assert summary["action_types"] == 5  # 5種類の動作

    def test_generate_summary_empty(self, formatter):
        """空のサマリー生成テスト"""
        summary = formatter._generate_summary([])

        assert summary["total_time"] == "00:00:00"
        assert summary["total_time_seconds"] == 0
        assert summary["step_count"] == 0
        assert summary["action_types"] == 0

    def test_generate_timeline(self, formatter, sample_steps):
        """タイムライン生成テスト"""
        timeline = formatter._generate_timeline(sample_steps)

        assert len(timeline) == 5
        assert timeline[0]["timestamp"] == "00:00:15"
        assert timeline[0]["action"] == "切る"
        assert timeline[0]["step_number"] == 1

    def test_count_actions(self, formatter, sample_steps):
        """動作カウントテスト"""
        actions = formatter._count_actions(sample_steps)

        assert actions["切る"] == 1
        assert actions["炒める"] == 1
        assert actions["加える"] == 1
        assert actions["煮る"] == 1
        assert actions["盛り付ける"] == 1

    def test_count_actions_duplicates(self, formatter):
        """重複動作カウントテスト"""
        steps = [
            TimestampedStep(1, "00:00:10", 10, "切る", "玉ねぎを切る", 0.9),
            TimestampedStep(2, "00:00:20", 20, "切る", "人参を切る", 0.9),
            TimestampedStep(3, "00:01:00", 60, "炒める", "炒める", 0.9),
        ]

        actions = formatter._count_actions(steps)
        assert actions["切る"] == 2
        assert actions["炒める"] == 1

    def test_format_for_frontend(self, formatter, sample_steps):
        """フロントエンド用フォーマットテスト"""
        result = formatter.format_for_frontend(
            video_url="https://youtube.com/watch?v=test",
            title="テスト料理",
            steps=sample_steps,
            thumbnail_url="https://example.com/thumb.jpg",
            description="テスト説明",
        )

        assert "video" in result
        assert result["video"]["url"] == "https://youtube.com/watch?v=test"
        assert result["video"]["thumbnail"] == "https://example.com/thumb.jpg"
        assert result["video"]["title"] == "テスト料理"
        assert result["video"]["description"] == "テスト説明"

        assert "recipe" in result
        assert len(result["recipe"]["steps"]) == 5
        assert result["recipe"]["totalSteps"] == 5
        assert result["recipe"]["estimatedTime"] == "00:04:30"

        assert "navigation" in result
        assert "chapters" in result["navigation"]
        assert "quickJump" in result["navigation"]

    def test_generate_chapters(self, formatter):
        """チャプター生成テスト"""
        steps = [
            TimestampedStep(1, "00:00:10", 10, "切る", "玉ねぎを切る", 0.9),
            TimestampedStep(2, "00:00:20", 20, "切る", "人参を切る", 0.9),
            TimestampedStep(3, "00:01:00", 60, "炒める", "炒める", 0.9),
            TimestampedStep(4, "00:02:00", 120, "煮る", "煮る", 0.9),
        ]

        chapters = formatter._generate_chapters(steps)

        assert len(chapters) == 3
        assert chapters[0]["title"] == "切る"
        assert chapters[0]["start"] == "00:00:10"
        assert chapters[0]["steps"] == [1, 2]

        assert chapters[1]["title"] == "炒める"
        assert chapters[1]["steps"] == [3]

    def test_generate_quick_jump(self, formatter, sample_steps):
        """クイックジャンプ生成テスト"""
        quick_jump = formatter._generate_quick_jump(sample_steps)

        # 主要な調理動作のみ抽出
        assert len(quick_jump) > 0
        assert all(
            item["action"] in {"切る", "炒める", "煮る", "焼く", "揚げる"}
            for item in quick_jump
        )

        # 同じ動作は1回のみ
        actions = [item["action"] for item in quick_jump]
        assert len(actions) == len(set(actions))

    def test_export_import_json(self, formatter, sample_steps, tmp_path):
        """JSON エクスポート/インポートテスト"""
        data = formatter.format_recipe(
            video_url="https://youtube.com/watch?v=test",
            title="テスト料理",
            steps=sample_steps,
        )

        # エクスポート
        output_path = tmp_path / "recipe.json"
        formatter.export_to_json(data, str(output_path))

        # ファイルが存在することを確認
        assert output_path.exists()

        # インポート
        imported = formatter.import_from_json(str(output_path))

        assert imported["video_url"] == data["video_url"]
        assert imported["title"] == data["title"]
        assert imported["total_steps"] == data["total_steps"]

    def test_format_srt_subtitles(self, formatter):
        """SRT字幕フォーマットテスト"""
        steps = [
            TimestampedStep(1, "00:00:10", 10, "切る", "玉ねぎを切る", 0.9),
            TimestampedStep(2, "00:01:00", 60, "炒める", "炒める", 0.9),
        ]

        srt = formatter.format_srt_subtitles(steps)

        assert "1\n" in srt
        assert "00:00:10,000 --> " in srt
        assert "[切る] 玉ねぎを切る" in srt
        assert "2\n" in srt
        assert "[炒める] 炒める" in srt

    def test_generate_markdown_recipe(self, formatter, sample_steps):
        """Markdown レシピ生成テスト"""
        markdown = formatter.generate_markdown_recipe(
            video_url="https://youtube.com/watch?v=test",
            title="テスト料理",
            steps=sample_steps,
        )

        assert "# テスト料理" in markdown
        assert "**動画URL**: https://youtube.com/watch?v=test" in markdown
        assert "## 手順" in markdown
        assert "**[00:00:15]** *切る*: 玉ねぎを薄切りにします" in markdown
        assert "## サマリー" in markdown
        assert "総調理時間: 00:04:30" in markdown


class TestIntegration:
    """統合テスト"""

    def test_full_workflow(self):
        """完全なワークフローテスト"""
        # 1. トランスクリプトを生成
        transcript = """
00:00:15 玉ねぎを薄切りにします
00:00:45 フライパンで玉ねぎを炒めます
00:01:30 豚肉を加えて炒めます
00:02:00 醤油とみりんを加えます
00:03:15 弱火で5分煮込みます
00:04:30 お皿に盛り付けて完成です
    """

        # 2. タイムスタンプ付き手順を生成
        generator = TimestampGenerator()
        steps = generator.generate_timestamped_steps(transcript)

        assert len(steps) > 0

        # 3. レシピをフォーマット
        formatter = RecipeFormatter()
        recipe = formatter.format_recipe(
            video_url="https://youtube.com/watch?v=test",
            title="豚の生姜焼き",
            steps=steps,
        )

        assert recipe["total_steps"] == len(steps)
        assert "summary" in recipe
        assert "timeline" in recipe

        # 4. フロントエンド用フォーマット
        frontend_data = formatter.format_for_frontend(
            video_url="https://youtube.com/watch?v=test",
            title="豚の生姜焼き",
            steps=steps,
        )

        assert "video" in frontend_data
        assert "recipe" in frontend_data
        assert "navigation" in frontend_data

    def test_workflow_with_merge(self):
        """統合＋近接手順統合テスト"""
        transcript = """
00:00:10 玉ねぎを切ります
00:00:15 人参を切ります
00:00:20 ピーマンを切ります
00:01:00 野菜を炒めます
    """

        generator = TimestampGenerator()
        steps = generator.generate_timestamped_steps(transcript)

        # 近接手順を統合
        merged_steps = generator.merge_similar_steps(steps, time_threshold=10)

        # 統合後の手順数が減ることを確認
        assert len(merged_steps) < len(steps)

        formatter = RecipeFormatter()
        recipe = formatter.format_recipe(
            video_url="https://youtube.com/watch?v=test",
            title="野菜炒め",
            steps=merged_steps,
        )

        assert recipe["total_steps"] == len(merged_steps)
