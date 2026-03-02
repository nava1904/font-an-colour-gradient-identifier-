"""Font identification service using Hugging Face font classifier."""

from typing import Dict, Any, Optional
from io import BytesIO

from PIL import Image

# Lazy load to avoid slow startup
_classifier = None
_classifier_error: Optional[str] = None


def _get_classifier():
    """Lazy-load the font classifier pipeline."""
    global _classifier, _classifier_error
    if _classifier_error:
        return None
    if _classifier is None:
        try:
            from transformers import pipeline

            _classifier = pipeline(
                "image-classification",
                model="dchen0/font_classifier_v4",
                top_k=5,
            )
        except Exception as e:
            _classifier_error = str(e)
            return None
    return _classifier


def identify_font(image_bytes: bytes) -> Dict[str, Any]:
    """
    Identify font from image using DINOv2-based font classifier.
    Returns dict with label, confidence, and alternatives.
    """
    try:
        classifier = _get_classifier()
        if classifier is None:
            return {
                "label": "Unknown",
                "confidence": 0.0,
                "alternatives": [],
                "error": f"Font model unavailable: {_classifier_error or 'Not loaded'}",
            }
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
        results = classifier(img)

        if not results:
            return {
                "label": "Unknown",
                "confidence": 0.0,
                "alternatives": [],
                "error": "No predictions returned",
            }

        # Results are list of {"label": str, "score": float}
        top = results[0]
        alternatives = [
            {"label": r["label"], "score": round(float(r["score"]), 4)}
            for r in results[1:]
        ]

        return {
            "label": top["label"],
            "confidence": round(float(top["score"]), 4),
            "alternatives": alternatives,
        }
    except Exception as e:
        return {
            "label": "Unknown",
            "confidence": 0.0,
            "alternatives": [],
            "error": str(e),
        }
