"""
backend/routers/predict.py
POST /predict — accepts an image file, returns land cover classification.

Response shape (matches what ImageUploader.jsx already expects):
{
    "predicted_class": "Forest",
    "confidence": 0.923,
    "model": "ViT-B/16 · EuroSAT",
    "probabilities": {
        "AnnualCrop": 0.012,
        "Forest": 0.923,
        ...
    },
    "inference_time": "0.84s"
}
"""

import io
import time
from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image

from backend.core.model_manager import model_manager
from backend.core.config import settings

router = APIRouter()


@router.post("/predict")
async def predict(image: UploadFile = File(...)):

    # ── 1. Validate content type ──────────────────────────────────────────────
    if image.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file type: {image.content_type}. "
                   f"Allowed: {settings.ALLOWED_CONTENT_TYPES}",
        )

    # ── 2. Validate file size ─────────────────────────────────────────────────
    contents = await image.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.1f}MB. Max allowed: {settings.MAX_IMAGE_SIZE_MB}MB",
        )

    # ── 3. Decode image ───────────────────────────────────────────────────────
    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(
            status_code=422,
            detail=f"Could not decode image: {str(e)}",
        )

    # ── 4. Run inference ──────────────────────────────────────────────────────
    try:
        start = time.perf_counter()
        result = model_manager.vit.predict(pil_image, return_probabilities=True)
        elapsed = time.perf_counter() - start
        result["inference_time"] = f"{elapsed:.2f}s"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Inference failed: {str(e)}",
        )

    return result
