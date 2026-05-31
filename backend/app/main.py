from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.core.database import engine
from app.models import Base
from app.routes import health, cameras, heartbeats, traffic


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Database Initialization on Startup ---
    async with engine.begin() as conn:
        # Create all tables if they do not exist
        await conn.run_sync(Base.metadata.create_all)
        
        # Turn tables into TimescaleDB hypertables
        # Using Safe 'if_not_exists => TRUE' syntax
        await conn.execute(text("SELECT create_hypertable('heartbeats', 'timestamp', if_not_exists => TRUE);"))
        await conn.execute(text("SELECT create_hypertable('traffic_data', 'timestamp', if_not_exists => TRUE);"))
        await conn.execute(text("SELECT create_hypertable('camera_status_logs', 'timestamp', if_not_exists => TRUE);"))
        
    yield
    # --- Shutdown logic ---
    await engine.dispose()


app = FastAPI(
    title="Traffic Quality Platform",
    description="Real-time observability and validation for traffic surveillance networks",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health.router)
app.include_router(cameras.router)
app.include_router(heartbeats.router)
app.include_router(traffic.router)


@app.get("/")
async def root() -> dict:
    return {
        "service": "Traffic Quality Platform",
        "version": "0.1.0",
        "environment": settings.environment,
        "docs": "/docs",
    }
