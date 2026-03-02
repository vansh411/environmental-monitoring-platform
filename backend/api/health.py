"""backend/api/health.py"""
from fastapi import APIRouter
from backend.core.model_manager import model_manager

router = APIRouter()

@router.get("/health")
def health_check():
    return {
        "status": "ok",
        "model_loaded": model_manager.is_loaded,
        "model_path": model_manager.model_path,
        "api": "GeoSentinel v1.0.0",
    }
