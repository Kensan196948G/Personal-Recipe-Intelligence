"""
ImageDownloadService のテスト
"""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock
from backend.services.image_download_service import ImageDownloadService


class TestImageDownloadService:
    """ImageDownloadServiceのテスト"""

    @pytest.fixture
    def service(self, tmp_path):
        """テスト用サービスインスタンス（一時ディレクトリを使用）"""
        return ImageDownloadService(save_dir=str(tmp_path / "images"))

    # URL検証テスト
    def test_validate_url_valid_http(self, service):
        """有効なHTTP URLの検証"""
        assert service._validate_url("http://example.com/image.jpg") is True

    def test_validate_url_valid_https(self, service):
        """有効なHTTPS URLの検証"""
        assert service._validate_url("https://example.com/image.png") is True

    def test_validate_url_invalid_scheme(self, service):
        """無効なスキームのURLの検証"""
        assert service._validate_url("ftp://example.com/image.jpg") is False

    def test_validate_url_invalid_format(self, service):
        """無効なフォーマットのURLの検証"""
        assert service._validate_url("not-a-url") is False
        assert service._validate_url("") is False
        assert service._validate_url("http://") is False

    # 拡張子抽出テスト（URL）
    def test_get_extension_from_url_jpg(self, service):
        """URLからJPG拡張子を抽出"""
        assert service._get_extension_from_url("http://example.com/photo.jpg") == ".jpg"

    def test_get_extension_from_url_png(self, service):
        """URLからPNG拡張子を抽出"""
        assert service._get_extension_from_url("https://example.com/image.png") == ".png"

    def test_get_extension_from_url_gif(self, service):
        """URLからGIF拡張子を抽出"""
        assert service._get_extension_from_url("http://example.com/anim.gif") == ".gif"

    def test_get_extension_from_url_webp(self, service):
        """URLからWebP拡張子を抽出"""
        assert service._get_extension_from_url("http://example.com/image.webp") == ".webp"

    def test_get_extension_from_url_uppercase(self, service):
        """大文字拡張子の正規化"""
        assert service._get_extension_from_url("http://example.com/photo.JPG") == ".jpg"

    def test_get_extension_from_url_invalid(self, service):
        """無効な拡張子の場合"""
        assert service._get_extension_from_url("http://example.com/file.txt") is None
        assert service._get_extension_from_url("http://example.com/noext") is None

    # 拡張子抽出テスト（Content-Type）
    def test_get_extension_from_content_type_jpeg(self, service):
        """Content-TypeからJPEG拡張子を抽出"""
        assert service._get_extension_from_content_type("image/jpeg") == ".jpg"

    def test_get_extension_from_content_type_png(self, service):
        """Content-TypeからPNG拡張子を抽出"""
        assert service._get_extension_from_content_type("image/png") == ".png"

    def test_get_extension_from_content_type_with_charset(self, service):
        """charsetが含まれるContent-Type"""
        assert service._get_extension_from_content_type("image/jpeg; charset=utf-8") == ".jpg"

    def test_get_extension_from_content_type_invalid(self, service):
        """無効なContent-Type"""
        assert service._get_extension_from_content_type("text/html") is None

    # ファイル名生成テスト
    def test_generate_filename(self, service):
        """ファイル名生成のテスト"""
        filename = service._generate_filename(123, "http://example.com/photo.jpg", ".jpg")
        assert filename.startswith("123_")
        assert filename.endswith(".jpg")
        assert len(filename) == len("123_") + 8 + len(".jpg")  # 123_<8文字>.jpg

    def test_generate_filename_unique(self, service):
        """異なるURLで異なるファイル名が生成されることを確認"""
        filename1 = service._generate_filename(1, "http://example.com/a.jpg", ".jpg")
        filename2 = service._generate_filename(1, "http://example.com/b.jpg", ".jpg")
        assert filename1 != filename2  # 異なるURLなので異なるファイル名

    def test_generate_filename_same_url(self, service):
        """同じURLで同じファイル名が生成されることを確認（冪等性）"""
        filename1 = service._generate_filename(1, "http://example.com/a.jpg", ".jpg")
        filename2 = service._generate_filename(1, "http://example.com/a.jpg", ".jpg")
        assert filename1 == filename2  # 同じURLなので同じファイル名（冪等性）

    # ダウンロードテスト（モック）
    @pytest.mark.asyncio
    async def test_download_and_save_success_jpg(self, service):
        """正常なJPG画像ダウンロードのテスト"""
        with patch("httpx.AsyncClient") as mock_client:
            # モックレスポンス
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"\xff\xd8\xff\xe0" + b"\x00" * 100  # JPEG header + dummy
            mock_response.headers = {"content-type": "image/jpeg"}

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            # テスト実行
            result = await service.download_and_save("https://example.com/image.jpg", 1)

            # 結果検証
            assert result is not None
            assert Path(result).exists()
            assert Path(result).suffix == ".jpg"

    @pytest.mark.asyncio
    async def test_download_and_save_success_png(self, service):
        """正常なPNG画像ダウンロードのテスト"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # PNG header + dummy
            mock_response.headers = {"content-type": "image/png"}

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/image.png", 2)

            assert result is not None
            assert Path(result).exists()
            assert Path(result).suffix == ".png"

    @pytest.mark.asyncio
    async def test_download_and_save_invalid_url(self, service):
        """無効なURLでのダウンロードテスト"""
        result = await service.download_and_save("invalid-url", 1)
        assert result is None

    @pytest.mark.asyncio
    async def test_download_and_save_http_404(self, service):
        """HTTP 404エラー時のテスト"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 404

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/notfound.png", 1)
            assert result is None

    @pytest.mark.asyncio
    async def test_download_and_save_http_500(self, service):
        """HTTP 500エラー時のテスト"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 500

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/error.png", 1)
            assert result is None

    @pytest.mark.asyncio
    async def test_download_and_save_file_too_large(self, service):
        """ファイルサイズ超過時のテスト"""
        with patch("httpx.AsyncClient") as mock_client:
            # 11MB のファイル（制限は10MB）
            large_content = b"\x00" * (11 * 1024 * 1024)
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = large_content
            mock_response.headers = {"content-type": "image/jpeg"}

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/large.jpg", 1)
            assert result is None

    @pytest.mark.asyncio
    async def test_download_and_save_no_extension_from_url(self, service):
        """URLに拡張子がない場合、Content-Typeから推定"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"\xff\xd8\xff\xe0" + b"\x00" * 100
            mock_response.headers = {"content-type": "image/jpeg"}

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/image", 1)
            assert result is not None
            assert Path(result).suffix == ".jpg"

    @pytest.mark.asyncio
    async def test_download_and_save_invalid_content_type(self, service):
        """無効なContent-Typeの場合"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.content = b"dummy"
            mock_response.headers = {"content-type": "text/html"}

            mock_get = AsyncMock(return_value=mock_response)
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/noext", 1)
            assert result is None

    @pytest.mark.asyncio
    async def test_download_and_save_network_error(self, service):
        """ネットワークエラー時のテスト"""
        with patch("httpx.AsyncClient") as mock_client:
            mock_get = AsyncMock(side_effect=Exception("Network error"))
            mock_client.return_value.__aenter__.return_value.get = mock_get

            result = await service.download_and_save("https://example.com/image.jpg", 1)
            assert result is None

    # 拡張子チェックテスト
    def test_allowed_extensions(self, service):
        """許可された拡張子のチェック"""
        assert ".jpg" in service.ALLOWED_EXTENSIONS
        assert ".jpeg" in service.ALLOWED_EXTENSIONS
        assert ".png" in service.ALLOWED_EXTENSIONS
        assert ".gif" in service.ALLOWED_EXTENSIONS
        assert ".webp" in service.ALLOWED_EXTENSIONS
        assert ".exe" not in service.ALLOWED_EXTENSIONS
        assert ".pdf" not in service.ALLOWED_EXTENSIONS
