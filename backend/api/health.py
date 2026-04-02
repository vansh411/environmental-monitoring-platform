"""
backend/api/health.py
"""
from fastapi import APIRouter
from backend.core.model_manager import model_manager

router = APIRouter()


@router.get("/health")
def health_check():
    model_info = model_manager.get_model_info()
    return {
        "status":       "ok" if model_info["loaded"] else "degraded",
        "model_loaded": model_info["loaded"],
        "model_path":   model_info["path"],
        "model_format": model_info["format"],
        "api":          "GeoSentinel v1.0.0",
    }
