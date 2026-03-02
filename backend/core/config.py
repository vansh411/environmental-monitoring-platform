from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── Model ─────────────────────────────────────────────────────────────────
    # Weights-only checkpoint — what ModelCheckpoint(save_weights_only=True) saves
    MODEL_PATH: str = "./models/checkpoints/best_model.keras"

    # Fallback: full saved model if you ran vit.save_model() manually
    MODEL_PATH_FALLBACK: str = "./models/eurosat_vit.keras"

    # ── API ───────────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ── CORS ──────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
    ]

    # ── Image ─────────────────────────────────────────────────────────────────
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_CONTENT_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/tiff",
        "image/bmp",
        "image/webp",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
