"""
backend/api/predict.py
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

    # Guard: return clean 503 if model isn't loaded yet
    if not model_manager.is_loaded:
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded yet. Please retry in a few seconds.",
        )

    # ── Validate content type ──────────────────────────────────────────────────
    if image.content_type not in settings.ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=415,
            detail=(
                f"Unsupported file type: {image.content_type}. "
                f"Allowed: {settings.ALLOWED_CONTENT_TYPES}"
            ),
        )

    # ── Read and size-check ────────────────────────────────────────────────────
    contents = await image.read()
    size_mb  = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"File too large: {size_mb:.1f} MB. Max: {settings.MAX_IMAGE_SIZE_MB} MB",
        )

    # ── Decode image ───────────────────────────────────────────────────────────
    try:
        pil_image = Image.open(io.BytesIO(contents)).convert("RGB")
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not decode image: {e}")

    # ── Run inference ──────────────────────────────────────────────────────────
    try:
        start  = time.perf_counter()
        result = model_manager.vit.predict(pil_image, return_probabilities=True)
        result["inference_time"] = f"{time.perf_counter() - start:.3f}s"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {e}")

    return result
