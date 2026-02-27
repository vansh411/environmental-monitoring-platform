"""
FastAPI Backend — Environmental Monitoring Platform
Entry point: backend/main.py

Run with:
    uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend.api import classes, health
from backend.core.config import settings
from backend.core.model_manager import model_manager
from backend.api import predict


# ── Lifespan: runs once at startup and once at shutdown ───────────────────────
# This is the correct modern FastAPI pattern — replaces @app.on_event("startup")
@asynccontextmanager
async def lifespan(app: FastAPI):
    # STARTUP — load model into memory once
    print("\n" + "="*50)
    print("  GeoSentinel API starting up...")
    print("="*50)
    model_manager.load()
    print("="*50 + "\n")
    yield
    # SHUTDOWN — cleanup if needed
    print("\nGeoSentinel API shutting down.")


# ── App instance ──────────────────────────────────────────────────────────────
app = FastAPI(
    title="GeoSentinel — Environmental Monitoring API",
    description="AI-powered land cover classification using Vision Transformers and Sentinel-2 imagery.",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows your React frontend (localhost:3000) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(health.router,   tags=["Health"])
app.include_router(predict.router,  tags=["Prediction"])
app.include_router(classes.router,  tags=["Classes"])
