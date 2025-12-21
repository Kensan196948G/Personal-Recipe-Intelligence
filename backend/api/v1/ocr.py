"""
OCR API Endpoints - Rate Limited (5 requests/minute)

Handles image upload and text extraction for recipe OCR.
"""

from fastapi import APIRouter, Request, UploadFile, File
from typing import Dict, Any
import logging

from backend.middleware.rate_limiter import ocr_rate_limit

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/ocr", tags=["OCR"])


@router.post("/upload")
@ocr_rate_limit()
async def ocr_upload(request: Request, file: UploadFile = File(...)) -> Dict[str, Any]:
  """
  Upload image for OCR processing.
  Rate limit: 5 requests/minute (expensive operation)

  Args:
    request: FastAPI request object
    file: Image file to process

  Returns:
    JSON response with upload status
  """
  logger.info(
    f"OCR upload request from {request.client.host}",
    extra={"filename": file.filename, "content_type": file.content_type}
  )

  return {
    "status": "ok",
    "data": {
      "message": "OCR upload endpoint - not yet implemented",
      "filename": file.filename
    },
    "error": None
  }


@router.post("/extract")
@ocr_rate_limit()
async def ocr_extract(request: Request) -> Dict[str, Any]:
  """
  Extract text from uploaded image.
  Rate limit: 5 requests/minute (expensive operation)

  Args:
    request: FastAPI request object

  Returns:
    JSON response with extracted text
  """
  logger.info(f"OCR extract request from {request.client.host}")

  return {
    "status": "ok",
    "data": {
      "message": "OCR extract endpoint - not yet implemented"
    },
    "error": None
  }
