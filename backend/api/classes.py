"""backend/api/classes.py"""
from fastapi import APIRouter
from backend.ml.vit_model import CLASS_NAMES

router = APIRouter()

@router.get("/classes")
def get_classes():
    return {"classes": CLASS_NAMES, "total": len(CLASS_NAMES)}
