"""Analysis API route."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.font_service import identify_font
from app.services.color_service import extract_all_colors

router = APIRouter(prefix="/api", tags=["analyze"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
FONT_TIMEOUT_SECONDS = 60  # Font model can take long on first load

_executor = ThreadPoolExecutor(max_workers=2)


@router.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """
    Analyze uploaded image for font and color information.
    Returns font identification, dominant colors, gradient stops, and exact color samples.
    """
    if image.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_CONTENT_TYPES)}",
        )

    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)} MB",
        )

    if not contents:
        raise HTTPException(status_code=400, detail="Empty file")

    try:
        # Run color extraction first (fast, ~1–2 seconds)
        colors_result = extract_all_colors(contents)

        # Run font identification with timeout (model download can take 5+ min on first run)
        loop = asyncio.get_event_loop()
        try:
            font_result = await asyncio.wait_for(
                loop.run_in_executor(_executor, identify_font, contents),
                timeout=FONT_TIMEOUT_SECONDS,
            )
        except asyncio.TimeoutError:
            font_result = {
                "label": "Unknown",
                "confidence": 0.0,
                "alternatives": [],
                "error": "Font analysis timed out. The model may still be downloading on first run—try again in a few minutes.",
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

    return {
        "font": font_result,
        "colors": colors_result,
    }
