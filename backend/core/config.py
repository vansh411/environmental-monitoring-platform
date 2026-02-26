"""
backend/core/config.py
Central config — edit values here, they propagate everywhere.
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # ── Model ─────────────────────────────────────────────────────────────────
    # Path to your trained model — relative to project root
    MODEL_PATH: str = "./models/checkpoints/best_model.keras"

    # Fallback: if the above doesn't exist, try the final saved model
    MODEL_PATH_FALLBACK: str = "./models/eurosat_vit.keras"

    # ── API ───────────────────────────────────────────────────────────────────
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000

    # ── CORS ──────────────────────────────────────────────────────────────────
    # Add your frontend URL here — default covers local React dev server
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite
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
        env_file = ".env"           # optional: override any value via .env file
        env_file_encoding = "utf-8"


settings = Settings()
