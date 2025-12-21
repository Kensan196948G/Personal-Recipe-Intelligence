"""
TranscriptParserのテスト
"""

from backend.video.transcript_parser import TranscriptParser
from backend.video.models import TimestampedStep


class TestTranscriptParser:
    """TranscriptParserのテストクラス"""

    def setup_method(self):
        """各テストメソッド実行前の初期化"""
        self.parser = TranscriptParser()

    def test_extract_ingredients_with_quantities(self):
        """数量付き材料の抽出テスト"""
        text = "玉ねぎ 200グラム、にんじん 1本、豚肉 300g を用意します"
        ingredients = self.parser.extract_ingredients(text)

        assert len(ingredients) > 0
        assert any("玉ねぎ" in ing and "200" in ing for ing in ingredients)
        assert any("豚肉" in ing and "300" in ing for ing in ingredients)

    def test_extract_ingredients_no_quantities(self):
        """数量なしのテキストでは材料が抽出されない"""
        text = "今日は良い天気ですね"
        ingredients = self.parser.extract_ingredients(text)

        assert len(ingredients) == 0

    def test_extract_steps_with_keywords(self):
        """キーワードベースの手順抽出テスト"""
        transcript_data = [
            {"text": "まず玉ねぎを切ります", "start": 10.0, "duration": 3.0},
            {"text": "薄くスライスしてください", "start": 13.0, "duration": 2.0},
            {"text": "次に炒めます", "start": 15.0, "duration": 2.0},
            {"text": "中火で5分ほど", "start": 17.0, "duration": 2.0},
            {"text": "最後に塩コショウで味付けします", "start": 19.0, "duration": 3.0},
        ]

        steps = self.parser.extract_steps(transcript_data)

        assert len(steps) > 0
        assert isinstance(steps[0], TimestampedStep)
        assert steps[0].timestamp is not None
        assert steps[0].step_number == 1

    def test_extract_steps_by_time_segments(self):
        """時間区切りでの手順抽出テスト"""
        transcript_data = [
            {"text": "玉ねぎを切ります", "start": 0.0, "duration": 2.0},
            {"text": "薄くスライス", "start": 2.0, "duration": 2.0},
            {"text": "炒めます", "start": 40.0, "duration": 2.0},
            {"text": "中火で", "start": 42.0, "duration": 2.0},
            {"text": "味付けします", "start": 80.0, "duration": 2.0},
        ]

        steps = self.parser._extract_steps_by_time_segments(
            transcript_data, segment_duration=30
        )

        assert len(steps) >= 2  # 少なくとも2つの手順に分かれる
        assert steps[0].timestamp_seconds == 0
        assert steps[1].timestamp_seconds >= 30

    def test_extract_servings(self):
        """分量抽出のテスト"""
        text = "今日は4人分のカレーを作ります"
        servings = self.parser.extract_servings(text)

        assert servings is not None
        assert "4" in servings
        assert "人分" in servings

    def test_extract_servings_not_found(self):
        """分量が見つからない場合"""
        text = "カレーを作ります"
        servings = self.parser.extract_servings(text)

        assert servings is None

    def test_extract_cooking_time(self):
        """調理時間抽出のテスト"""
        text = "調理時間は30分です"
        cooking_time = self.parser.extract_cooking_time(text)

        assert cooking_time is not None
        assert "30" in cooking_time
        assert "分" in cooking_time

    def test_extract_cooking_time_not_found(self):
        """調理時間が見つからない場合"""
        text = "カレーを作ります"
        cooking_time = self.parser.extract_cooking_time(text)

        assert cooking_time is None

    def test_format_timestamp(self):
        """タイムスタンプのフォーマットテスト"""
        # 65秒 = 01:05
        timestamp = self.parser._format_timestamp(65.0)
        assert timestamp == "01:05"

        # 0秒 = 00:00
        timestamp = self.parser._format_timestamp(0.0)
        assert timestamp == "00:00"

        # 125秒 = 02:05
        timestamp = self.parser._format_timestamp(125.0)
        assert timestamp == "02:05"

        # None = 00:00
        timestamp = self.parser._format_timestamp(None)
        assert timestamp == "00:00"

    def test_parse_recipe_full(self):
        """完全なレシピ解析テスト"""
        transcript_text = """
    4人分のカレーを作ります。調理時間は30分です。
    玉ねぎ 200g、にんじん 1本、豚肉 300g を使います。
    まず野菜を切ります。次に炒めます。最後に煮込みます。
    """

        transcript_data = [
            {"text": "4人分のカレーを作ります", "start": 0.0, "duration": 3.0},
            {"text": "調理時間は30分です", "start": 3.0, "duration": 2.0},
            {"text": "玉ねぎ 200g を使います", "start": 5.0, "duration": 2.0},
            {"text": "まず野菜を切ります", "start": 10.0, "duration": 2.0},
            {"text": "次に炒めます", "start": 12.0, "duration": 2.0},
            {"text": "最後に煮込みます", "start": 14.0, "duration": 2.0},
        ]

        result = self.parser.parse_recipe(transcript_text, transcript_data)

        assert result is not None
        assert "ingredients" in result
        assert "steps" in result
        assert "servings" in result
        assert "cooking_time" in result

        # 分量が抽出されている
        assert result["servings"] is not None
        assert "4人分" in result["servings"]

        # 調理時間が抽出されている
        assert result["cooking_time"] is not None
        assert "30分" in result["cooking_time"]

        # 手順が抽出されている
        assert len(result["steps"]) > 0
