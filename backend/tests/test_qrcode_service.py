"""
QRCode Service Test

QRコード生成サービスのテストコード
"""

import pytest
from io import BytesIO
from PIL import Image

from backend.services.qrcode_service import QRCodeService


@pytest.fixture
def qrcode_service():
    """QRCodeServiceのフィクスチャ"""
    return QRCodeService(base_url="http://localhost:8000")


class TestQRCodeService:
    """QRCodeServiceのテストクラス"""

    def test_generate_recipe_url(self, qrcode_service):
        """レシピURL生成のテスト"""
        recipe_id = 123
        url = qrcode_service.generate_recipe_url(recipe_id)
        assert url == "http://localhost:8000/recipe/123"

    def test_generate_recipe_data(self, qrcode_service):
        """レシピデータ生成のテスト"""
        recipe_id = 123
        recipe_data = {
            "name": "カレーライス",
            "url": "https://example.com/curry",
            "ingredients": ["玉ねぎ", "じゃがいも", "にんじん"],
            "steps": ["野菜を切る", "炒める", "煮込む"],
        }

        data = qrcode_service.generate_recipe_data(recipe_id, recipe_data)
        assert '"id":123' in data
        assert '"name":"カレーライス"' in data
        assert '"ingredients"' in data
        assert '"steps"' in data

    def test_create_qrcode(self, qrcode_service):
        """QRCodeオブジェクト生成のテスト"""
        data = "https://example.com/test"
        qr = qrcode_service.create_qrcode(data)
        assert qr is not None
        assert qr.data_list is not None

    def test_generate_qrcode_image(self, qrcode_service):
        """QRコード画像生成のテスト"""
        data = "https://example.com/test"
        img = qrcode_service.generate_qrcode_image(data)
        assert isinstance(img, Image.Image)
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_generate_qrcode_image_with_style(self, qrcode_service):
        """スタイル付きQRコード画像生成のテスト"""
        import pytest

        data = "https://example.com/test"

        # Square style（デフォルト）は常に動作
        img_square = qrcode_service.generate_qrcode_image(data, style="square")
        assert isinstance(img_square, Image.Image)

        # Rounded/Circle スタイルはqrcodeライブラリバージョンによってサポートが異なる
        # エラーにならなければOK、エラーの場合はスキップ
        try:
            img_rounded = qrcode_service.generate_qrcode_image(data, style="rounded")
            assert isinstance(img_rounded, Image.Image)
        except (TypeError, ValueError):
            pytest.skip("Rounded style not supported in current qrcode version")

        try:
            img_circle = qrcode_service.generate_qrcode_image(data, style="circle")
            assert isinstance(img_circle, Image.Image)
        except (TypeError, ValueError):
            pytest.skip("Circle style not supported in current qrcode version")

    def test_generate_qrcode_image_with_colors(self, qrcode_service):
        """カラーカスタマイズQRコード画像生成のテスト"""
        data = "https://example.com/test"
        img = qrcode_service.generate_qrcode_image(
            data, fill_color="blue", back_color="yellow"
        )
        assert isinstance(img, Image.Image)

    def test_generate_qrcode_png_bytes(self, qrcode_service):
        """QRコードPNGバイト生成のテスト"""
        data = "https://example.com/test"
        png_bytes = qrcode_service.generate_qrcode_png_bytes(data)
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0

        # バイトデータから画像を読み込めるか確認
        img = Image.open(BytesIO(png_bytes))
        assert img.format == "PNG"

    def test_generate_qrcode_svg(self, qrcode_service):
        """QRコードSVG生成のテスト"""
        data = "https://example.com/test"
        svg_content = qrcode_service.generate_qrcode_svg(data)
        assert isinstance(svg_content, str)
        assert "<svg" in svg_content
        assert "</svg>" in svg_content

    def test_generate_recipe_qrcode_url_png(self, qrcode_service):
        """レシピURL用QRコード生成のテスト（PNG）"""
        recipe_id = 456
        png_bytes = qrcode_service.generate_recipe_qrcode_url(recipe_id, format="png")
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0

    def test_generate_recipe_qrcode_url_svg(self, qrcode_service):
        """レシピURL用QRコード生成のテスト（SVG）"""
        recipe_id = 456
        svg_content = qrcode_service.generate_recipe_qrcode_url(recipe_id, format="svg")
        assert isinstance(svg_content, str)
        assert "<svg" in svg_content

    def test_generate_recipe_qrcode_data_png(self, qrcode_service):
        """レシピデータ用QRコード生成のテスト（PNG）"""
        recipe_id = 789
        recipe_data = {
            "name": "パスタ",
            "url": "https://example.com/pasta",
            "ingredients": ["パスタ", "トマトソース"],
            "steps": ["茹でる", "和える"],
        }

        png_bytes = qrcode_service.generate_recipe_qrcode_data(
            recipe_id, recipe_data, format="png"
        )
        assert isinstance(png_bytes, bytes)
        assert len(png_bytes) > 0

    def test_generate_recipe_qrcode_data_svg(self, qrcode_service):
        """レシピデータ用QRコード生成のテスト（SVG）"""
        recipe_id = 789
        recipe_data = {
            "name": "パスタ",
            "url": "https://example.com/pasta",
            "ingredients": ["パスタ", "トマトソース"],
            "steps": ["茹でる", "和える"],
        }

        svg_content = qrcode_service.generate_recipe_qrcode_data(
            recipe_id, recipe_data, format="svg"
        )
        assert isinstance(svg_content, str)
        assert "<svg" in svg_content

    def test_qrcode_size_customization(self, qrcode_service):
        """QRコードサイズカスタマイズのテスト"""
        data = "https://example.com/test"

        # 小さいサイズ
        img_small = qrcode_service.generate_qrcode_image(data, box_size=5, border=2)
        assert isinstance(img_small, Image.Image)

        # 大きいサイズ
        img_large = qrcode_service.generate_qrcode_image(data, box_size=20, border=8)
        assert isinstance(img_large, Image.Image)

        # サイズ比較
        assert img_large.size[0] > img_small.size[0]

    def test_base_url_customization(self):
        """ベースURLカスタマイズのテスト"""
        custom_service = QRCodeService(base_url="https://example.com")
        url = custom_service.generate_recipe_url(123)
        assert url == "https://example.com/recipe/123"

    def test_base_url_trailing_slash(self):
        """ベースURLの末尾スラッシュ処理のテスト"""
        custom_service = QRCodeService(base_url="https://example.com/")
        url = custom_service.generate_recipe_url(123)
        assert url == "https://example.com/recipe/123"
