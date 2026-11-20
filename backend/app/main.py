from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.core.config import settings
from app.api.v1.api import api_router
from app.core.init_db import init_database

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Mount local storage for generated figures and PDF artifacts
os.makedirs(settings.STORAGE_DIR, exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "artifacts"), exist_ok=True)
os.makedirs(os.path.join(settings.STORAGE_DIR, "reports"), exist_ok=True)
app.mount("/api/v1/storage", StaticFiles(directory=settings.STORAGE_DIR), name="storage")

@app.on_event("startup")
async def startup_event():
    await init_database()

@app.get("/healthz", tags=["System"])
async def health_check():
    return {
        "status": "online",
        "service": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
        "version": settings.VERSION
    }
