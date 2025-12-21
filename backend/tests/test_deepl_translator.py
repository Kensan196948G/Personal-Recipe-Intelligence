"""
DeepL Translator のテスト

DeepLTranslator の以下の機能をテスト:
- 初期化とエンドポイント選択
- 単一テキスト翻訳
- バッチ翻訳
- API使用量取得
- リトライ機構
- エラーハンドリング
- 空文字列処理

目標カバレッジ: 90%
テスト関数数: 20-30
"""

import pytest
import httpx
from unittest.mock import Mock, MagicMock, patch
from tenacity import RetryError

from backend.services.deepl_translator import DeepLTranslator, should_retry_http_error


# ================================================================================
# Fixtures
# ================================================================================

@pytest.fixture
def translator_free():
    """Free API Translator"""
    return DeepLTranslator(api_key="test_key:fx")


@pytest.fixture
def translator_pro():
    """Pro API Translator"""
    return DeepLTranslator(api_key="test_pro_key")


@pytest.fixture
def mock_httpx_client():
    """モック httpx.Client"""
    with patch("backend.services.deepl_translator.httpx.Client") as mock:
        client = MagicMock()
        mock.return_value.__enter__ = Mock(return_value=client)
        mock.return_value.__exit__ = Mock(return_value=False)
        yield client


# ================================================================================
# 初期化テスト (5 tests)
# ================================================================================

def test_init_with_free_api_key():
    """Free APIキーで初期化"""
    translator = DeepLTranslator(api_key="my_free_key:fx")

    assert translator.api_key == "my_free_key:fx"
    assert translator.base_url == "https://api-free.deepl.com/v2"


def test_init_with_pro_api_key():
    """Pro APIキーで初期化"""
    translator = DeepLTranslator(api_key="my_pro_key")

    assert translator.api_key == "my_pro_key"
    assert translator.base_url == "https://api.deepl.com/v2"


def test_init_with_env_var():
    """環境変数からAPIキー取得"""
    with patch.dict("os.environ", {"DEEPL_API_KEY": "env_key:fx"}):
        translator = DeepLTranslator()

        assert translator.api_key == "env_key:fx"
        assert translator.base_url == "https://api-free.deepl.com/v2"


def test_init_without_api_key():
    """APIキーなしでエラー"""
    with patch.dict("os.environ", {}, clear=True):
        with pytest.raises(ValueError, match="DEEPL_API_KEY is required"):
            DeepLTranslator()


def test_init_api_key_passed_priority():
    """引数のAPIキーが環境変数より優先"""
    with patch.dict("os.environ", {"DEEPL_API_KEY": "env_key"}):
        translator = DeepLTranslator(api_key="arg_key")

        assert translator.api_key == "arg_key"


# ================================================================================
# 単一翻訳テスト (7 tests)
# ================================================================================

def test_translate_success(translator_pro, mock_httpx_client):
    """翻訳成功"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [{"text": "こんにちは"}]
    }
    mock_httpx_client.post.return_value = mock_response

    result = translator_pro.translate("Hello", target_lang="JA")

    assert result == "こんにちは"
    mock_httpx_client.post.assert_called_once()
    call_kwargs = mock_httpx_client.post.call_args.kwargs
    assert call_kwargs["data"]["text"] == "Hello"
    assert call_kwargs["data"]["target_lang"] == "JA"


def test_translate_with_source_lang(translator_pro, mock_httpx_client):
    """ソース言語指定あり"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [{"text": "Translation"}]
    }
    mock_httpx_client.post.return_value = mock_response

    result = translator_pro.translate("Text", target_lang="EN", source_lang="JA")

    call_kwargs = mock_httpx_client.post.call_args.kwargs
    assert call_kwargs["data"]["source_lang"] == "JA"


def test_translate_empty_string(translator_pro, mock_httpx_client):
    """空文字列は翻訳しない"""
    result = translator_pro.translate("", target_lang="JA")

    assert result == ""
    mock_httpx_client.post.assert_not_called()


def test_translate_whitespace_only(translator_pro, mock_httpx_client):
    """空白のみは翻訳しない"""
    result = translator_pro.translate("   ", target_lang="JA")

    assert result == ""
    mock_httpx_client.post.assert_not_called()


def test_translate_http_error(translator_pro, mock_httpx_client):
    """HTTPエラー"""
    mock_response = Mock()
    mock_response.status_code = 400
    mock_response.text = "Bad request"
    mock_httpx_client.post.side_effect = httpx.HTTPStatusError(
        "Error", request=Mock(), response=mock_response
    )

    with pytest.raises(httpx.HTTPStatusError):
        translator_pro.translate("Text", target_lang="JA")


def test_translate_general_exception(translator_pro, mock_httpx_client):
    """一般的な例外"""
    mock_httpx_client.post.side_effect = Exception("Network error")

    with pytest.raises(Exception, match="Network error"):
        translator_pro.translate("Text", target_lang="JA")


def test_translate_authorization_header(translator_pro, mock_httpx_client):
    """Authorizationヘッダーが正しい"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [{"text": "Translated"}]
    }
    mock_httpx_client.post.return_value = mock_response

    translator_pro.translate("Text", target_lang="JA")

    call_kwargs = mock_httpx_client.post.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "DeepL-Auth-Key test_pro_key"


# ================================================================================
# バッチ翻訳テスト (8 tests)
# ================================================================================

def test_translate_batch_success(translator_pro, mock_httpx_client):
    """バッチ翻訳成功"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [
            {"text": "翻訳1"},
            {"text": "翻訳2"},
            {"text": "翻訳3"},
        ]
    }
    mock_httpx_client.post.return_value = mock_response

    texts = ["Text 1", "Text 2", "Text 3"]
    result = translator_pro.translate_batch(texts, target_lang="JA")

    assert result == ["翻訳1", "翻訳2", "翻訳3"]


def test_translate_batch_empty_list(translator_pro, mock_httpx_client):
    """空リスト"""
    result = translator_pro.translate_batch([], target_lang="JA")

    assert result == []
    mock_httpx_client.post.assert_not_called()


def test_translate_batch_with_empty_strings(translator_pro, mock_httpx_client):
    """空文字列を含むリスト"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [
            {"text": "翻訳1"},
            {"text": "翻訳2"},
        ]
    }
    mock_httpx_client.post.return_value = mock_response

    texts = ["Text 1", "", "Text 2", "   "]
    result = translator_pro.translate_batch(texts, target_lang="JA")

    assert len(result) == 4
    assert result[0] == "翻訳1"
    assert result[1] == ""
    assert result[2] == "翻訳2"
    assert result[3] == ""


def test_translate_batch_all_empty(translator_pro, mock_httpx_client):
    """全て空文字列"""
    texts = ["", "  ", ""]
    result = translator_pro.translate_batch(texts, target_lang="JA")

    assert result == ["", "", ""]
    mock_httpx_client.post.assert_not_called()


def test_translate_batch_with_source_lang(translator_pro, mock_httpx_client):
    """ソース言語指定"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [{"text": "翻訳"}]
    }
    mock_httpx_client.post.return_value = mock_response

    translator_pro.translate_batch(["Text"], target_lang="JA", source_lang="EN")

    call_kwargs = mock_httpx_client.post.call_args.kwargs
    assert call_kwargs["data"]["source_lang"] == "EN"


def test_translate_batch_http_error(translator_pro, mock_httpx_client):
    """HTTPエラー"""
    mock_response = Mock()
    mock_response.status_code = 500
    mock_response.text = "Server error"
    mock_httpx_client.post.side_effect = httpx.HTTPStatusError(
        "Error", request=Mock(), response=mock_response
    )

    with pytest.raises(httpx.HTTPStatusError):
        translator_pro.translate_batch(["Text 1", "Text 2"], target_lang="JA")


def test_translate_batch_general_exception(translator_pro, mock_httpx_client):
    """一般的な例外"""
    mock_httpx_client.post.side_effect = Exception("Batch error")

    with pytest.raises(Exception, match="Batch error"):
        translator_pro.translate_batch(["Text"], target_lang="JA")


def test_translate_batch_timeout(translator_pro, mock_httpx_client):
    """タイムアウトが60秒"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "translations": [{"text": "翻訳"}]
    }
    mock_httpx_client.post.return_value = mock_response

    translator_pro.translate_batch(["Text"], target_lang="JA")

    # httpx.Client のタイムアウトが60秒
    with patch("backend.services.deepl_translator.httpx.Client") as mock_client_cls:
        mock_client_cls.assert_called_with(timeout=60.0)


# ================================================================================
# API使用量取得テスト (4 tests)
# ================================================================================

def test_get_usage_success(translator_pro, mock_httpx_client):
    """使用量取得成功"""
    mock_response = Mock()
    mock_response.json.return_value = {
        "character_count": 12345,
        "character_limit": 500000,
    }
    mock_httpx_client.get.return_value = mock_response

    result = translator_pro.get_usage()

    assert result["character_count"] == 12345
    assert result["character_limit"] == 500000
    mock_httpx_client.get.assert_called_once()


def test_get_usage_endpoint(translator_pro, mock_httpx_client):
    """正しいエンドポイント"""
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_httpx_client.get.return_value = mock_response

    translator_pro.get_usage()

    call_args = mock_httpx_client.get.call_args
    assert call_args[0][0] == "https://api.deepl.com/v2/usage"


def test_get_usage_authorization(translator_pro, mock_httpx_client):
    """Authorizationヘッダー"""
    mock_response = Mock()
    mock_response.json.return_value = {}
    mock_httpx_client.get.return_value = mock_response

    translator_pro.get_usage()

    call_kwargs = mock_httpx_client.get.call_args.kwargs
    assert call_kwargs["headers"]["Authorization"] == "DeepL-Auth-Key test_pro_key"


def test_get_usage_exception(translator_pro, mock_httpx_client):
    """例外処理"""
    mock_httpx_client.get.side_effect = Exception("Usage check failed")

    with pytest.raises(Exception, match="Usage check failed"):
        translator_pro.get_usage()


# ================================================================================
# リトライ機構テスト (5 tests)
# ================================================================================

def test_should_retry_429_error():
    """429エラーはリトライ"""
    mock_response = Mock()
    mock_response.status_code = 429
    exception = httpx.HTTPStatusError("Too many requests", request=Mock(), response=mock_response)

    assert should_retry_http_error(exception) is True


def test_should_retry_500_error():
    """500エラーはリトライ"""
    mock_response = Mock()
    mock_response.status_code = 500
    exception = httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response)

    assert should_retry_http_error(exception) is True


def test_should_retry_503_error():
    """503エラーはリトライ"""
    mock_response = Mock()
    mock_response.status_code = 503
    exception = httpx.HTTPStatusError("Service unavailable", request=Mock(), response=mock_response)

    assert should_retry_http_error(exception) is True


def test_should_not_retry_400_error():
    """400エラーはリトライしない"""
    mock_response = Mock()
    mock_response.status_code = 400
    exception = httpx.HTTPStatusError("Bad request", request=Mock(), response=mock_response)

    assert should_retry_http_error(exception) is False


def test_should_not_retry_non_http_error():
    """HTTPStatusError以外はリトライしない"""
    exception = ValueError("Invalid input")

    assert should_retry_http_error(exception) is False
