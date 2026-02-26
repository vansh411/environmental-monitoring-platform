"""
backend/core/model_manager.py

Loads the ViT model ONCE at startup and holds it in memory.
All prediction requests share the same instance — no per-request loading.
"""

from pathlib import Path
from backend.core.config import settings


class ModelManager:
    def __init__(self):
        self._vit = None          # populated by load()
        self._model_path = None   # which path was actually used

    # ─────────────────────────────────────────────────────────────────────────
    def load(self):
        """
        Called once during FastAPI lifespan startup.
        Tries MODEL_PATH first, falls back to MODEL_PATH_FALLBACK.
        Raises RuntimeError if neither exists — fail fast rather than
        serve wrong predictions silently.
        """
        # Import here to avoid TF loading before startup
        from backend.ml.vit_model import ViTModel

        primary  = Path(settings.MODEL_PATH)
        fallback = Path(settings.MODEL_PATH_FALLBACK)

        if primary.exists():
            path = primary
        elif fallback.exists():
            print(f"⚠ Primary model not found, using fallback: {fallback}")
            path = fallback
        else:
            raise RuntimeError(
                f"No trained model found.\n"
                f"  Tried: {primary}\n"
                f"  Tried: {fallback}\n"
                f"  Run train_model.py first."
            )

        self._vit = ViTModel(model_path=str(path))
        self._model_path = path
        print(f"✓ Model ready — loaded from: {path}")

    # ─────────────────────────────────────────────────────────────────────────
    @property
    def vit(self):
        if self._vit is None:
            raise RuntimeError("Model not loaded. Did startup complete?")
        return self._vit

    @property
    def is_loaded(self) -> bool:
        return self._vit is not None

    @property
    def model_path(self) -> str:
        return str(self._model_path) if self._model_path else "not loaded"


# ── Singleton — imported by all routers ───────────────────────────────────────
model_manager = ModelManager()
