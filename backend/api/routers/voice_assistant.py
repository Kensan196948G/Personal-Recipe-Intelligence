"""
Voice Assistant API Router - 音声アシスタント連携エンドポイント
"""

from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
import logging

from backend.services.voice_assistant_service import VoiceAssistantService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice", tags=["voice-assistant"])

# サービスインスタンス
voice_service = VoiceAssistantService()


class AlexaRequest(BaseModel):
    """Alexa Skills Kit リクエスト"""

    version: str
    session: Dict[str, Any]
    request: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None


class GoogleRequest(BaseModel):
    """Google Actions リクエスト"""

    handler: Dict[str, Any]
    intent: Dict[str, Any]
    scene: Dict[str, Any]
    session: Dict[str, Any]
    user: Dict[str, Any]
    device: Optional[Dict[str, Any]] = None


class GenericVoiceCommand(BaseModel):
    """汎用音声コマンド"""

    session_id: str = Field(..., description="セッションID")
    command: str = Field(..., description="音声コマンドテキスト")
    language: str = Field(default="ja-JP", description="言語コード")


class VoiceCommandResponse(BaseModel):
    """音声コマンドレスポンス"""

    status: str
    speech: str
    message: Optional[str] = None
    should_end_session: bool = False
    data: Optional[Dict[str, Any]] = None


@router.post("/alexa", summary="Alexa Skill エンドポイント")
async def alexa_webhook(
    request: AlexaRequest,
    signature: Optional[str] = Header(None, alias="Signature"),
    signature_cert_chain_url: Optional[str] = Header(
        None, alias="SignatureCertChainUrl"
    ),
) -> Dict[str, Any]:
    """
    Alexa Skills Kit からのリクエストを処理

    - Alexa Skills Kit の署名検証は省略（本番環境では必須）
    - インテントに基づいてレシピ操作を実行
    - SSML形式の音声応答を返却
    """
    try:
        logger.info(f"Alexa request received: {request.request.get('type')}")

        # Note: Alexa request signature verification
        # In production, verify the request signature for security
        # TODO: Implement Alexa signature verification
        # from backend.services.alexa_verifier import verify_alexa_signature
        # verify_alexa_signature(signature, signature_cert_chain_url, request)

        response = voice_service.process_alexa_request(request.dict())

        logger.info(
            f"Alexa response: {response.get('response', {}).get('outputSpeech')}"
        )

        return response

    except Exception as e:
        logger.error(f"Error in Alexa webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google", summary="Google Action エンドポイント")
async def google_webhook(request: GoogleRequest) -> Dict[str, Any]:
    """
    Google Actions からのリクエストを処理

    - Conversational Actions 形式に対応
    - インテントに基づいてレシピ操作を実行
    - SSML形式の音声応答を返却
    """
    try:
        logger.info(f"Google request received: {request.handler.get('name')}")

        response = voice_service.process_google_request(request.dict())

        logger.info(f"Google response: {response.get('prompt', {})}")

        return response

    except Exception as e:
        logger.error(f"Error in Google webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/generic", summary="汎用音声コマンド", response_model=VoiceCommandResponse
)
async def generic_voice_command(command: GenericVoiceCommand) -> VoiceCommandResponse:
    """
    汎用音声コマンドを処理（Web Speech API など）

    - ブラウザの音声認識結果を処理
    - 簡易的な自然言語処理でインテント抽出
    - 音声応答テキストを返却
    """
    try:
        logger.info(f"Generic command received: {command.command}")

        result = voice_service.process_generic_command(
            command.session_id, command.command
        )

        return VoiceCommandResponse(**result)

    except Exception as e:
        logger.error(f"Error in generic command: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/intents", summary="対応インテント一覧")
async def get_intents() -> Dict[str, Any]:
    """
    音声アシスタントが対応するインテント一覧を返却

    - レシピ検索、手順読み上げ、タイマー設定など
    - 各インテントの説明とサンプルフレーズ
    """
    try:
        intents = voice_service.get_supported_intents()

        return {"status": "ok", "data": {"intents": intents, "total": len(intents)}}

    except Exception as e:
        logger.error(f"Error getting intents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}", summary="セッション削除")
async def delete_session(session_id: str) -> Dict[str, str]:
    """
    特定セッションを削除

    - 音声アシスタントのセッション情報をクリア
    """
    try:
        if session_id in voice_service.sessions:
            del voice_service.sessions[session_id]
            voice_service._save_sessions()

            return {"status": "ok", "message": f"Session {session_id} deleted"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions/cleanup", summary="古いセッションクリーンアップ")
async def cleanup_sessions() -> Dict[str, Any]:
    """
    24時間以上アクセスのないセッションを削除

    - 定期的なメンテナンスに使用
    """
    try:
        before_count = len(voice_service.sessions)
        voice_service.cleanup_sessions()
        after_count = len(voice_service.sessions)

        cleaned = before_count - after_count

        return {
            "status": "ok",
            "data": {"cleaned_sessions": cleaned, "remaining_sessions": after_count},
        }

    except Exception as e:
        logger.error(f"Error cleaning up sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", summary="セッション一覧")
async def get_sessions() -> Dict[str, Any]:
    """
    アクティブなセッション一覧を取得

    - デバッグ・管理用
    """
    try:
        sessions_info = []

        for session_id, session in voice_service.sessions.items():
            sessions_info.append(
                {
                    "session_id": session_id,
                    "created_at": session.get("created_at"),
                    "last_access": session.get("last_access"),
                    "current_recipe_id": session.get("current_recipe_id"),
                    "current_step_index": session.get("current_step_index"),
                }
            )

        return {
            "status": "ok",
            "data": {"sessions": sessions_info, "total": len(sessions_info)},
        }

    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ヘルスチェック
@router.get("/health", summary="音声アシスタントサービスヘルスチェック")
async def health_check() -> Dict[str, str]:
    """音声アシスタントサービスの稼働状態確認"""
    return {
        "status": "ok",
        "service": "voice_assistant",
        "message": "Voice assistant service is running",
    }
