"""
backend/core/model_manager.py
"""

from pathlib import Path
from backend.core.config import settings


class ModelManager:
    def __init__(self):
        self._vit = None
        self._model_path = None

    def load(self):
        from backend.ml.vit_model import ViTModel

        primary  = Path(settings.MODEL_PATH)
        fallback = Path(settings.MODEL_PATH_FALLBACK)

        if primary.exists():
            path = primary
        elif fallback.exists():
            print(f"⚠ Primary not found, using fallback: {fallback}")
            path = fallback
        else:
            raise RuntimeError(
                f"No trained model found.\n"
                f"  Tried: {primary}\n"
                f"  Tried: {fallback}\n"
                f"  Run train_model.py first."
            )

        self._model_path = path

        # The error 'no item named model.weights.h5 in archive' confirms
        # best_model.keras is a full saved model (architecture + weights)
        # NOT a weights-only file — so load it with model_path, not weights_path
        self._vit = ViTModel(model_path=str(path))
        print(f"✓ Model ready — {path}")

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


# Singleton
model_manager = ModelManager()
