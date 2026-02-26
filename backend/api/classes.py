"""
backend/routers/classes.py
GET /classes — returns all 10 EuroSAT land cover class names.
Frontend can call this once on load to populate any dropdowns/legends.
"""

from fastapi import APIRouter
from backend.ml.vit_model import CLASS_NAMES

router = APIRouter()


@router.get("/classes")
def get_classes():
    return {
        "classes": CLASS_NAMES,
        "total": len(CLASS_NAMES),
    }
