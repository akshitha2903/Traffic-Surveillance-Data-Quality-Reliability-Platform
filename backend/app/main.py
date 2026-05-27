from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routes import health

app = FastAPI(
    title="Traffic Quality Platform",
    description="Real-time observability and validation for traffic surveillance networks",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "Traffic Quality Platform",
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs",
    }
