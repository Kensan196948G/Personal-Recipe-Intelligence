"""
Voice Assistant Service のテスト
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta

from backend.services.voice_assistant_service import (
    VoiceAssistantService,
    VoiceAssistant,
    IntentType,
)


@pytest.fixture
def temp_data_dir(tmp_path):
    """一時データディレクトリ"""
    return str(tmp_path / "voice_test")


@pytest.fixture
def voice_service(temp_data_dir):
    """音声アシスタントサービスインスタンス"""
    return VoiceAssistantService(data_dir=temp_data_dir)


class TestVoiceAssistantService:
    """VoiceAssistantService のテスト"""

    def test_initialization(self, voice_service, temp_data_dir):
        """初期化テスト"""
        assert voice_service.data_dir == Path(temp_data_dir)
        assert voice_service.sessions == {}
        # sessions_file はセッション保存時に作成される
        assert voice_service.sessions_file is not None

    def test_session_creation(self, voice_service):
        """セッション作成テスト"""
        session_id = "test_session_123"
        session = voice_service._get_or_create_session(session_id)

        assert session["session_id"] == session_id
        assert "created_at" in session
        assert "last_access" in session
        assert session["current_recipe_id"] is None
        assert session["current_step_index"] == 0
        assert session["context"] == {}

    def test_session_update(self, voice_service):
        """セッション更新テスト"""
        session_id = "test_session_update"
        voice_service._get_or_create_session(session_id)

        updates = {"current_recipe_id": "recipe_001", "current_step_index": 2}
        voice_service._update_session(session_id, updates)

        session = voice_service.sessions[session_id]
        assert session["current_recipe_id"] == "recipe_001"
        assert session["current_step_index"] == 2

    def test_session_persistence(self, voice_service):
        """セッション永続化テスト"""
        session_id = "test_session_persist"
        voice_service._get_or_create_session(session_id)
        voice_service._update_session(session_id, {"current_recipe_id": "recipe_123"})

        # 新しいサービスインスタンスで読み込み
        new_service = VoiceAssistantService(data_dir=str(voice_service.data_dir))
        assert session_id in new_service.sessions
        assert new_service.sessions[session_id]["current_recipe_id"] == "recipe_123"

    def test_cleanup_old_sessions(self, voice_service):
        """古いセッションクリーンアップテスト"""
        # 古いセッション作成
        old_session_id = "old_session"
        old_time = (datetime.now() - timedelta(hours=25)).isoformat()
        voice_service.sessions[old_session_id] = {
            "session_id": old_session_id,
            "created_at": old_time,
            "last_access": old_time,
            "current_recipe_id": None,
            "current_step_index": 0,
            "context": {},
        }

        # 新しいセッション作成
        new_session_id = "new_session"
        voice_service._get_or_create_session(new_session_id)

        # クリーンアップ実行
        voice_service._cleanup_old_sessions(max_age_hours=24)

        assert old_session_id not in voice_service.sessions
        assert new_session_id in voice_service.sessions

    def test_alexa_launch_request(self, voice_service):
        """Alexa起動リクエストテスト"""
        request_data = {
            "version": "1.0",
            "session": {"sessionId": "test_alexa_session"},
            "request": {"type": "LaunchRequest"},
        }

        response = voice_service.process_alexa_request(request_data)

        assert response["version"] == "1.0"
        assert "response" in response
        assert "outputSpeech" in response["response"]
        assert response["response"]["outputSpeech"]["type"] == "SSML"
        assert (
            "レシピアシスタントへようこそ"
            in response["response"]["outputSpeech"]["ssml"]
        )

    def test_alexa_intent_request_search_recipe(self, voice_service):
        """Alexa レシピ検索インテントテスト"""
        request_data = {
            "version": "1.0",
            "session": {"sessionId": "test_alexa_session"},
            "request": {
                "type": "IntentRequest",
                "intent": {
                    "name": IntentType.SEARCH_RECIPE,
                    "slots": {"query": {"value": "カレー"}},
                },
            },
        }

        response = voice_service.process_alexa_request(request_data)

        assert response["version"] == "1.0"
        assert "カレーのレシピを検索" in response["response"]["outputSpeech"]["ssml"]
        assert response["response"]["shouldEndSession"] is False

    def test_alexa_session_end_request(self, voice_service):
        """Alexa セッション終了リクエストテスト"""
        request_data = {
            "version": "1.0",
            "session": {"sessionId": "test_alexa_session"},
            "request": {"type": "SessionEndedRequest"},
        }

        response = voice_service.process_alexa_request(request_data)

        assert response["response"]["shouldEndSession"] is True

    def test_google_launch_request(self, voice_service):
        """Google起動リクエストテスト"""
        request_data = {
            "handler": {"name": "actions.intent.MAIN"},
            "intent": {},
            "scene": {},
            "session": {"id": "test_google_session"},
            "user": {},
        }

        response = voice_service.process_google_request(request_data)

        assert "prompt" in response
        assert "レシピアシスタントへようこそ" in response["prompt"]["content"]["speech"]

    def test_google_intent_request(self, voice_service):
        """Google インテントリクエストテスト"""
        request_data = {
            "handler": {"name": IntentType.HELP, "params": {}},
            "intent": {},
            "scene": {},
            "session": {"id": "test_google_session"},
            "user": {},
        }

        response = voice_service.process_google_request(request_data)

        assert "prompt" in response
        assert "レシピアシスタント" in response["prompt"]["content"]["speech"]

    def test_generic_command_search_recipe(self, voice_service):
        """汎用コマンド - レシピ検索テスト"""
        session_id = "test_generic_session"
        command = "カレーのレシピを教えて"

        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "カレー" in response["speech"]
        assert "レシピ" in response["speech"]

    def test_generic_command_next_step(self, voice_service):
        """汎用コマンド - 次の手順テスト"""
        session_id = "test_generic_session"

        # まずレシピを設定
        voice_service._update_session(
            session_id,
            {
                "current_recipe_id": "recipe_001",
                "current_step_index": 0,
                "context": {"steps": ["手順1", "手順2", "手順3"]},
            },
        )

        command = "次"
        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "手順2" in response["speech"]

    def test_generic_command_previous_step(self, voice_service):
        """汎用コマンド - 前の手順テスト"""
        session_id = "test_generic_session"

        # レシピ設定（手順2の状態）
        voice_service._update_session(
            session_id,
            {
                "current_recipe_id": "recipe_001",
                "current_step_index": 1,
                "context": {"steps": ["手順1", "手順2", "手順3"]},
            },
        )

        command = "前の手順"
        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "手順1" in response["speech"]

    def test_generic_command_repeat_step(self, voice_service):
        """汎用コマンド - 手順繰り返しテスト"""
        session_id = "test_generic_session"

        voice_service._update_session(
            session_id,
            {
                "current_recipe_id": "recipe_001",
                "current_step_index": 1,
                "context": {"steps": ["手順1", "手順2", "手順3"]},
            },
        )

        command = "もう一度"
        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "手順2" in response["speech"]

    def test_generic_command_ingredients(self, voice_service):
        """汎用コマンド - 材料取得テスト"""
        session_id = "test_generic_session"

        voice_service._update_session(session_id, {"current_recipe_id": "recipe_001"})

        command = "材料を教えて"
        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "材料" in response["speech"]

    def test_generic_command_timer(self, voice_service):
        """汎用コマンド - タイマー設定テスト"""
        session_id = "test_generic_session"
        command = "タイマー10分"

        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "10分" in response["speech"]
        assert "タイマー" in response["speech"]

    def test_generic_command_help(self, voice_service):
        """汎用コマンド - ヘルプテスト"""
        session_id = "test_generic_session"
        command = "ヘルプ"

        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "ok"
        assert "レシピアシスタント" in response["speech"]

    def test_generic_command_unknown(self, voice_service):
        """汎用コマンド - 不明なコマンドテスト"""
        session_id = "test_generic_session"
        command = "意味不明なコマンド"

        response = voice_service.process_generic_command(session_id, command)

        assert response["status"] == "error"
        assert "理解できませんでした" in response["speech"]

    def test_get_supported_intents(self, voice_service):
        """対応インテント一覧取得テスト"""
        intents = voice_service.get_supported_intents()

        assert len(intents) > 0
        assert any(i["intent"] == IntentType.SEARCH_RECIPE for i in intents)
        assert any(i["intent"] == IntentType.NEXT_STEP for i in intents)
        assert any(i["intent"] == IntentType.SET_TIMER for i in intents)

        # 各インテントに必要な情報が含まれているか
        for intent in intents:
            assert "intent" in intent
            assert "description" in intent
            assert "parameters" in intent
            assert "examples" in intent

    def test_handle_next_step_at_end(self, voice_service):
        """最後の手順で「次」を実行したときのテスト"""
        session_id = "test_session_end"

        steps = ["手順1", "手順2", "手順3"]
        voice_service._update_session(
            session_id,
            {
                "current_recipe_id": "recipe_001",
                "current_step_index": 2,  # 最後の手順
                "context": {"steps": steps},
            },
        )

        response = voice_service._handle_next_step(
            voice_service.sessions[session_id], VoiceAssistant.GENERIC
        )

        assert "完了" in response["speech"] or "終了" in response["speech"]

    def test_handle_previous_step_at_start(self, voice_service):
        """最初の手順で「前」を実行したときのテスト"""
        session_id = "test_session_start"

        steps = ["手順1", "手順2", "手順3"]
        voice_service._update_session(
            session_id,
            {
                "current_recipe_id": "recipe_001",
                "current_step_index": 0,  # 最初の手順
                "context": {"steps": steps},
            },
        )

        response = voice_service._handle_previous_step(
            voice_service.sessions[session_id], VoiceAssistant.GENERIC
        )

        assert "最初" in response["speech"]

    def test_handle_ingredients_without_recipe(self, voice_service):
        """レシピ未選択状態で材料を取得しようとしたときのテスト"""
        session_id = "test_session_no_recipe"
        session = voice_service._get_or_create_session(session_id)

        response = voice_service._handle_get_ingredients(
            session, VoiceAssistant.GENERIC
        )

        assert "選択されていません" in response["speech"]

    def test_extract_alexa_slots(self, voice_service):
        """Alexa スロット抽出テスト"""
        slots = {
            "query": {"value": "カレー"},
            "duration": {"value": "5"},
            "empty_slot": {},
        }

        extracted = voice_service._extract_alexa_slots(slots)

        assert extracted["query"] == "カレー"
        assert extracted["duration"] == "5"
        assert "empty_slot" not in extracted

    def test_multiple_sessions(self, voice_service):
        """複数セッション同時管理テスト"""
        session_ids = ["session_1", "session_2", "session_3"]

        for session_id in session_ids:
            voice_service._get_or_create_session(session_id)
            voice_service._update_session(
                session_id, {"current_recipe_id": f"recipe_{session_id}"}
            )

        assert len(voice_service.sessions) == 3

        for session_id in session_ids:
            assert session_id in voice_service.sessions
            assert (
                voice_service.sessions[session_id]["current_recipe_id"]
                == f"recipe_{session_id}"
            )
