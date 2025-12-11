"""
Voice Assistant Service - Alexa / Google Actions 連携サービス

音声アシスタントからのリクエスト処理、インテント解析、応答生成を担当
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class VoiceAssistant(str, Enum):
  """音声アシスタント種別"""
  ALEXA = "alexa"
  GOOGLE = "google"
  GENERIC = "generic"


class IntentType(str, Enum):
  """インテント種別"""
  SEARCH_RECIPE = "SearchRecipe"
  GET_RECIPE_STEPS = "GetRecipeSteps"
  SET_TIMER = "SetTimer"
  GET_INGREDIENTS = "GetIngredients"
  NEXT_STEP = "NextStep"
  PREVIOUS_STEP = "PreviousStep"
  REPEAT_STEP = "RepeatStep"
  HELP = "Help"
  CANCEL = "Cancel"


class VoiceAssistantService:
  """音声アシスタントサービス"""

  def __init__(self, data_dir: str = "data/voice"):
    self.data_dir = Path(data_dir)
    self.data_dir.mkdir(parents=True, exist_ok=True)
    self.sessions_file = self.data_dir / "sessions.json"
    self.sessions: Dict[str, Dict[str, Any]] = self._load_sessions()

  def _load_sessions(self) -> Dict[str, Dict[str, Any]]:
    """セッションデータ読み込み"""
    if self.sessions_file.exists():
      try:
        with open(self.sessions_file, "r", encoding="utf-8") as f:
          return json.load(f)
      except Exception as e:
        logger.error(f"Failed to load sessions: {e}")
    return {}

  def _save_sessions(self):
    """セッションデータ保存"""
    try:
      with open(self.sessions_file, "w", encoding="utf-8") as f:
        json.dump(self.sessions, f, ensure_ascii=False, indent=2)
    except Exception as e:
      logger.error(f"Failed to save sessions: {e}")

  def _get_or_create_session(self, session_id: str) -> Dict[str, Any]:
    """セッション取得または作成"""
    if session_id not in self.sessions:
      self.sessions[session_id] = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "last_access": datetime.now().isoformat(),
        "current_recipe_id": None,
        "current_step_index": 0,
        "context": {}
      }
    else:
      self.sessions[session_id]["last_access"] = datetime.now().isoformat()

    return self.sessions[session_id]

  def _update_session(self, session_id: str, updates: Dict[str, Any]):
    """セッション更新"""
    session = self._get_or_create_session(session_id)
    session.update(updates)
    self._save_sessions()

  def _cleanup_old_sessions(self, max_age_hours: int = 24):
    """古いセッション削除"""
    cutoff = datetime.now() - timedelta(hours=max_age_hours)
    to_delete = []

    for session_id, session in self.sessions.items():
      last_access = datetime.fromisoformat(session["last_access"])
      if last_access < cutoff:
        to_delete.append(session_id)

    for session_id in to_delete:
      del self.sessions[session_id]

    if to_delete:
      self._save_sessions()
      logger.info(f"Cleaned up {len(to_delete)} old sessions")

  def process_alexa_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Alexa Skills Kit リクエスト処理"""
    try:
      request = request_data.get("request", {})
      session = request_data.get("session", {})
      session_id = session.get("sessionId", "unknown")

      request_type = request.get("type")

      if request_type == "LaunchRequest":
        return self._alexa_launch_response()
      elif request_type == "IntentRequest":
        intent = request.get("intent", {})
        intent_name = intent.get("name")
        slots = intent.get("slots", {})
        return self._process_intent(
          session_id,
          intent_name,
          self._extract_alexa_slots(slots),
          VoiceAssistant.ALEXA
        )
      elif request_type == "SessionEndedRequest":
        return self._alexa_end_response()
      else:
        return self._alexa_error_response("Unknown request type")

    except Exception as e:
      logger.error(f"Error processing Alexa request: {e}")
      return self._alexa_error_response(str(e))

  def process_google_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Google Actions リクエスト処理"""
    try:
      handler = request_data.get("handler", {})
      intent_name = handler.get("name")
      session_id = request_data.get("session", {}).get("id", "unknown")
      params = handler.get("params", {})

      if intent_name == "actions.intent.MAIN":
        return self._google_launch_response()
      else:
        return self._process_intent(
          session_id,
          intent_name,
          params,
          VoiceAssistant.GOOGLE
        )

    except Exception as e:
      logger.error(f"Error processing Google request: {e}")
      return self._google_error_response(str(e))

  def process_generic_command(
    self,
    session_id: str,
    command: str
  ) -> Dict[str, Any]:
    """汎用音声コマンド処理"""
    try:
      # 簡易的な意図解析
      command_lower = command.lower()

      if "レシピ" in command_lower or "recipe" in command_lower:
        # レシピ検索
        query = command_lower.replace("レシピ", "").replace("recipe", "").strip()
        return self._process_intent(
          session_id,
          IntentType.SEARCH_RECIPE,
          {"query": query},
          VoiceAssistant.GENERIC
        )
      elif "次" in command_lower or "next" in command_lower:
        return self._process_intent(
          session_id,
          IntentType.NEXT_STEP,
          {},
          VoiceAssistant.GENERIC
        )
      elif "前" in command_lower or "previous" in command_lower:
        return self._process_intent(
          session_id,
          IntentType.PREVIOUS_STEP,
          {},
          VoiceAssistant.GENERIC
        )
      elif "もう一度" in command_lower or "repeat" in command_lower:
        return self._process_intent(
          session_id,
          IntentType.REPEAT_STEP,
          {},
          VoiceAssistant.GENERIC
        )
      elif "材料" in command_lower or "ingredients" in command_lower:
        return self._process_intent(
          session_id,
          IntentType.GET_INGREDIENTS,
          {},
          VoiceAssistant.GENERIC
        )
      elif "タイマー" in command_lower or "timer" in command_lower:
        # タイマー設定（簡易的な時間抽出）
        import re
        minutes = re.search(r"(\d+)\s*分", command_lower)
        if minutes:
          duration = int(minutes.group(1))
        else:
          duration = 5  # デフォルト

        return self._process_intent(
          session_id,
          IntentType.SET_TIMER,
          {"duration": duration},
          VoiceAssistant.GENERIC
        )
      elif "ヘルプ" in command_lower or "help" in command_lower:
        return self._process_intent(
          session_id,
          IntentType.HELP,
          {},
          VoiceAssistant.GENERIC
        )
      else:
        return {
          "status": "error",
          "message": "コマンドを理解できませんでした",
          "speech": "すみません、コマンドを理解できませんでした。ヘルプと言ってみてください。"
        }

    except Exception as e:
      logger.error(f"Error processing generic command: {e}")
      return {
        "status": "error",
        "message": str(e),
        "speech": "エラーが発生しました"
      }

  def _process_intent(
    self,
    session_id: str,
    intent_name: str,
    parameters: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """インテント処理"""
    session = self._get_or_create_session(session_id)

    # インテント別処理
    if intent_name == IntentType.SEARCH_RECIPE:
      return self._handle_search_recipe(session, parameters, assistant)
    elif intent_name == IntentType.GET_RECIPE_STEPS:
      return self._handle_get_recipe_steps(session, parameters, assistant)
    elif intent_name == IntentType.GET_INGREDIENTS:
      return self._handle_get_ingredients(session, assistant)
    elif intent_name == IntentType.NEXT_STEP:
      return self._handle_next_step(session, assistant)
    elif intent_name == IntentType.PREVIOUS_STEP:
      return self._handle_previous_step(session, assistant)
    elif intent_name == IntentType.REPEAT_STEP:
      return self._handle_repeat_step(session, assistant)
    elif intent_name == IntentType.SET_TIMER:
      return self._handle_set_timer(session, parameters, assistant)
    elif intent_name == IntentType.HELP:
      return self._handle_help(assistant)
    elif intent_name == IntentType.CANCEL:
      return self._handle_cancel(session, assistant)
    else:
      return self._format_response(
        "そのコマンドには対応していません",
        assistant,
        should_end_session=False
      )

  def _handle_search_recipe(
    self,
    session: Dict[str, Any],
    parameters: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """レシピ検索"""
    query = parameters.get("query", "")

    # TODO: 実際のレシピ検索を実装
    # ここではダミーレスポンス
    speech = f"{query}のレシピを検索しています。カレーライス、ハヤシライス、ビーフシチューが見つかりました。どれにしますか？"

    # セッションにコンテキスト保存
    self._update_session(session["session_id"], {
      "context": {
        "last_search": query,
        "search_results": ["カレーライス", "ハヤシライス", "ビーフシチュー"]
      }
    })

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_get_recipe_steps(
    self,
    session: Dict[str, Any],
    parameters: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """レシピ手順取得"""
    recipe_id = parameters.get("recipe_id")

    # TODO: 実際のレシピ取得を実装
    # ダミーレシピ
    dummy_steps = [
      "玉ねぎとにんじんを一口大に切ります",
      "鍋に油を熱し、肉を炒めます",
      "野菜を加えてさらに炒めます",
      "水を加えて20分煮込みます",
      "カレールーを加えて溶かし、5分煮込みます"
    ]

    self._update_session(session["session_id"], {
      "current_recipe_id": recipe_id,
      "current_step_index": 0,
      "context": {
        "steps": dummy_steps
      }
    })

    speech = f"レシピを開始します。手順1: {dummy_steps[0]}"

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_get_ingredients(
    self,
    session: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """材料取得"""
    if not session.get("current_recipe_id"):
      speech = "レシピが選択されていません。まずレシピを検索してください。"
    else:
      # TODO: 実際の材料取得を実装
      speech = "材料は、玉ねぎ1個、にんじん1本、牛肉200グラム、カレールー1箱、水600ミリリットルです。"

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_next_step(
    self,
    session: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """次の手順"""
    steps = session.get("context", {}).get("steps", [])
    current_index = session.get("current_step_index", 0)

    if not steps:
      speech = "レシピが選択されていません"
    elif current_index >= len(steps) - 1:
      speech = "これで全ての手順が完了しました。お疲れ様でした！"
    else:
      next_index = current_index + 1
      self._update_session(session["session_id"], {
        "current_step_index": next_index
      })
      speech = f"手順{next_index + 1}: {steps[next_index]}"

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_previous_step(
    self,
    session: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """前の手順"""
    steps = session.get("context", {}).get("steps", [])
    current_index = session.get("current_step_index", 0)

    if not steps:
      speech = "レシピが選択されていません"
    elif current_index <= 0:
      speech = "これが最初の手順です"
    else:
      prev_index = current_index - 1
      self._update_session(session["session_id"], {
        "current_step_index": prev_index
      })
      speech = f"手順{prev_index + 1}: {steps[prev_index]}"

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_repeat_step(
    self,
    session: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """手順繰り返し"""
    steps = session.get("context", {}).get("steps", [])
    current_index = session.get("current_step_index", 0)

    if not steps:
      speech = "レシピが選択されていません"
    else:
      speech = f"手順{current_index + 1}: {steps[current_index]}"

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_set_timer(
    self,
    session: Dict[str, Any],
    parameters: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """タイマー設定"""
    duration = parameters.get("duration", 5)

    speech = f"{duration}分のタイマーをセットしました"

    # TODO: 実際のタイマー機能実装（プッシュ通知など）

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_help(self, assistant: VoiceAssistant) -> Dict[str, Any]:
    """ヘルプ"""
    speech = (
      "レシピアシスタントです。"
      "「カレーのレシピ」と言えばレシピを検索できます。"
      "「次」で次の手順、「前」で前の手順、「もう一度」で同じ手順を繰り返します。"
      "「材料」で材料リスト、「タイマー5分」でタイマーを設定できます。"
    )

    return self._format_response(speech, assistant, should_end_session=False)

  def _handle_cancel(
    self,
    session: Dict[str, Any],
    assistant: VoiceAssistant
  ) -> Dict[str, Any]:
    """キャンセル"""
    self._update_session(session["session_id"], {
      "current_recipe_id": None,
      "current_step_index": 0,
      "context": {}
    })

    speech = "レシピをキャンセルしました"

    return self._format_response(speech, assistant, should_end_session=True)

  def _format_response(
    self,
    speech_text: str,
    assistant: VoiceAssistant,
    should_end_session: bool = False,
    card_title: Optional[str] = None,
    card_content: Optional[str] = None
  ) -> Dict[str, Any]:
    """アシスタント別レスポンス形成"""
    if assistant == VoiceAssistant.ALEXA:
      return self._alexa_response(
        speech_text,
        should_end_session,
        card_title,
        card_content
      )
    elif assistant == VoiceAssistant.GOOGLE:
      return self._google_response(speech_text, should_end_session)
    else:
      return {
        "status": "ok",
        "speech": speech_text,
        "should_end_session": should_end_session
      }

  def _alexa_response(
    self,
    speech_text: str,
    should_end_session: bool = False,
    card_title: Optional[str] = None,
    card_content: Optional[str] = None
  ) -> Dict[str, Any]:
    """Alexa形式レスポンス"""
    response = {
      "version": "1.0",
      "response": {
        "outputSpeech": {
          "type": "SSML",
          "ssml": f"<speak>{speech_text}</speak>"
        },
        "shouldEndSession": should_end_session
      }
    }

    if card_title and card_content:
      response["response"]["card"] = {
        "type": "Simple",
        "title": card_title,
        "content": card_content
      }

    return response

  def _alexa_launch_response(self) -> Dict[str, Any]:
    """Alexa起動レスポンス"""
    speech = "レシピアシスタントへようこそ。レシピを検索するには、料理名を言ってください。"
    return self._alexa_response(speech, should_end_session=False)

  def _alexa_end_response(self) -> Dict[str, Any]:
    """Alexa終了レスポンス"""
    speech = "ありがとうございました。また使ってください。"
    return self._alexa_response(speech, should_end_session=True)

  def _alexa_error_response(self, error_message: str) -> Dict[str, Any]:
    """Alexaエラーレスポンス"""
    speech = "エラーが発生しました。もう一度お試しください。"
    logger.error(f"Alexa error: {error_message}")
    return self._alexa_response(speech, should_end_session=True)

  def _google_response(
    self,
    speech_text: str,
    should_end_session: bool = False
  ) -> Dict[str, Any]:
    """Google Actions形式レスポンス"""
    response = {
      "session": {
        "params": {}
      },
      "prompt": {
        "override": False,
        "content": {
          "speech": f"<speak>{speech_text}</speak>"
        }
      }
    }

    if should_end_session:
      response["scene"] = {
        "name": "actions.scene.END_CONVERSATION"
      }

    return response

  def _google_launch_response(self) -> Dict[str, Any]:
    """Google起動レスポンス"""
    speech = "レシピアシスタントへようこそ。レシピを検索するには、料理名を言ってください。"
    return self._google_response(speech, should_end_session=False)

  def _google_error_response(self, error_message: str) -> Dict[str, Any]:
    """Googleエラーレスポンス"""
    speech = "エラーが発生しました。もう一度お試しください。"
    logger.error(f"Google error: {error_message}")
    return self._google_response(speech, should_end_session=True)

  def _extract_alexa_slots(self, slots: Dict[str, Any]) -> Dict[str, Any]:
    """Alexaスロット値抽出"""
    extracted = {}
    for slot_name, slot_data in slots.items():
      if "value" in slot_data:
        extracted[slot_name] = slot_data["value"]
    return extracted

  def get_supported_intents(self) -> List[Dict[str, Any]]:
    """対応インテント一覧"""
    return [
      {
        "intent": IntentType.SEARCH_RECIPE,
        "description": "レシピ検索",
        "parameters": ["query"],
        "examples": ["カレーのレシピ", "パスタの作り方"]
      },
      {
        "intent": IntentType.GET_RECIPE_STEPS,
        "description": "レシピ手順取得",
        "parameters": ["recipe_id"],
        "examples": ["レシピを開始", "作り方を教えて"]
      },
      {
        "intent": IntentType.GET_INGREDIENTS,
        "description": "材料リスト取得",
        "parameters": [],
        "examples": ["材料は何？", "何が必要？"]
      },
      {
        "intent": IntentType.NEXT_STEP,
        "description": "次の手順",
        "parameters": [],
        "examples": ["次", "次の手順", "次へ"]
      },
      {
        "intent": IntentType.PREVIOUS_STEP,
        "description": "前の手順",
        "parameters": [],
        "examples": ["前", "戻る", "前の手順"]
      },
      {
        "intent": IntentType.REPEAT_STEP,
        "description": "手順繰り返し",
        "parameters": [],
        "examples": ["もう一度", "繰り返して", "もう一回"]
      },
      {
        "intent": IntentType.SET_TIMER,
        "description": "タイマー設定",
        "parameters": ["duration"],
        "examples": ["5分タイマー", "タイマー10分"]
      },
      {
        "intent": IntentType.HELP,
        "description": "ヘルプ",
        "parameters": [],
        "examples": ["ヘルプ", "使い方", "何ができる？"]
      },
      {
        "intent": IntentType.CANCEL,
        "description": "キャンセル",
        "parameters": [],
        "examples": ["キャンセル", "終了", "やめる"]
      }
    ]

  def cleanup_sessions(self):
    """古いセッションクリーンアップ"""
    self._cleanup_old_sessions()
