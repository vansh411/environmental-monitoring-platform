"""
backend/core/model_manager.py
"""
from pathlib import Path
from backend.core.config import settings


def _is_weights_only_file(path: Path) -> bool:
    """
    Detect whether a file is a weights-only checkpoint or a full saved model.

    Keras naming conventions:
      weights-only  →  *.weights.h5  |  *.weights.keras
      full model    →  *.keras       |  *.h5  (no '.weights.' in name)
    """
    return ".weights." in path.name


class ModelManager:
    def __init__(self):
        self._vit        = None
        self._model_path = None
        self._weights_only = True

    # ── Public API ─────────────────────────────────────────────────────────────

    def load(self):
        """
        Find the best available model file and load it into a ViTModel instance.

        Search order:
          1. settings.MODEL_PATH          →  best_model.weights.keras  (primary)
          2. settings.MODEL_PATH_FALLBACK →  eurosat_vit.keras         (fallback)
          3. Legacy .h5 equivalents of the above
        """
        from backend.ml.vit_model import ViTModel

        path         = self._resolve_model_path()
        weights_only = _is_weights_only_file(path)

        print(f"  Loading : {path}")
        print(f"  Format  : {'weights-only' if weights_only else 'full saved model'}")

        if weights_only:
            # Build the graph first, then load weights into it
            self._vit = ViTModel(
                num_classes=10,
                weights_path=str(path),
                freeze_backbone=True,
            )
        else:
            # Load architecture + weights together
            self._vit = ViTModel(
                num_classes=10,
                model_path=str(path),
                freeze_backbone=True,
            )

        self._model_path   = path
        self._weights_only = weights_only
        print("✓ Model ready")

    @property
    def vit(self):
        if self._vit is None:
            raise RuntimeError(
                "Model not loaded. Server startup may have failed — "
                "check the console for errors."
            )
        return self._vit

    @property
    def is_loaded(self) -> bool:
        return self._vit is not None

    @property
    def model_path(self) -> str:
        return str(self._model_path) if self._model_path else "not loaded"

    def get_model_info(self) -> dict:
        return {
            "loaded": self.is_loaded,
            "path":   self.model_path,
            "format": "weights-only" if self._weights_only else "full-model",
        }

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _resolve_model_path(self) -> Path:
        """
        Return the first existing model file from the candidate list.
        Raises RuntimeError with a clear fix instruction if nothing is found.
        """
        candidates = [
            Path(settings.MODEL_PATH),           # best_model.weights.keras  ← primary
            Path(settings.MODEL_PATH_FALLBACK),  # eurosat_vit.keras         ← fallback
            # Legacy .h5 names from older Keras / previous training runs
            Path("./models/checkpoints/best_model.weights.h5"),
            Path("./models/eurosat_vit.h5"),
        ]

        for path in candidates:
            if path.exists():
                print(f"✓ Found model: {path}")
                return path

        searched = "\n".join(f"    • {p}" for p in candidates)
        raise RuntimeError(
            f"\n"
            f"  ✗ No trained model file found.\n"
            f"  Searched:\n{searched}\n\n"
            f"  HOW TO FIX:\n"
            f"  Option A (Colab) : Train on Colab, download best_model.weights.keras,\n"
            f"                     copy to  ./models/checkpoints/\n"
            f"  Option B (local) : Run  python train_model.py  and wait for it to finish.\n"
        )


model_manager = ModelManager()
