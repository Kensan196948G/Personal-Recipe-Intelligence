"""
DeepL API Translator Service - 翻訳サービス
"""

import os
import logging
from typing import Optional

import httpx

logger = logging.getLogger(__name__)


class DeepLTranslator:
    """DeepL APIを使った翻訳サービス"""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")
        if not self.api_key:
            raise ValueError("DEEPL_API_KEY is required")

        # Free APIとPro APIでエンドポイントが異なる
        if self.api_key.endswith(":fx"):
            self.base_url = "https://api-free.deepl.com/v2"
        else:
            self.base_url = "https://api.deepl.com/v2"

    def translate(
        self,
        text: str,
        target_lang: str = "JA",
        source_lang: Optional[str] = None,
    ) -> str:
        """テキストを翻訳する"""
        if not text or not text.strip():
            return ""

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.post(
                    f"{self.base_url}/translate",
                    headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                    data={
                        "text": text,
                        "target_lang": target_lang,
                        **({"source_lang": source_lang} if source_lang else {}),
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result["translations"][0]["text"]
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepL API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Translation error: {e}")
            raise

    def translate_batch(
        self,
        texts: list[str],
        target_lang: str = "JA",
        source_lang: Optional[str] = None,
    ) -> list[str]:
        """複数テキストを一括翻訳する"""
        if not texts:
            return []

        # 空文字列を除外してインデックスを記録
        non_empty = [(i, t) for i, t in enumerate(texts) if t and t.strip()]
        if not non_empty:
            return [""] * len(texts)

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.base_url}/translate",
                    headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                    data={
                        "text": [t for _, t in non_empty],
                        "target_lang": target_lang,
                        **({"source_lang": source_lang} if source_lang else {}),
                    },
                )
                response.raise_for_status()
                result = response.json()

                # 結果を元の位置に配置
                translated = [""] * len(texts)
                for (orig_idx, _), trans in zip(
                    non_empty, result["translations"]
                ):
                    translated[orig_idx] = trans["text"]
                return translated

        except httpx.HTTPStatusError as e:
            logger.error(f"DeepL API error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Batch translation error: {e}")
            raise

    def get_usage(self) -> dict:
        """API使用量を取得"""
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    f"{self.base_url}/usage",
                    headers={"Authorization": f"DeepL-Auth-Key {self.api_key}"},
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"Usage check error: {e}")
            raise
