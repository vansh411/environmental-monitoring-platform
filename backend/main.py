"""
backend/main.py
Run: python -m uvicorn backend.main:app --reload --port 8000
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.core.config import settings
from backend.core.model_manager import model_manager
from backend.api import predict, health, classes


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("\n" + "=" * 50)
    print("  GeoSentinel API starting up...")
    print("=" * 50)
    model_manager.load()
    print("=" * 50 + "\n")
    yield
    print("\nGeoSentinel API shutting down.")


app = FastAPI(
    title="GeoSentinel — Environmental Monitoring API",
    description="AI-powered land cover classification using Vision Transformers.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,  tags=["Health"])
app.include_router(predict.router, tags=["Prediction"])
app.include_router(classes.router, tags=["Classes"])
