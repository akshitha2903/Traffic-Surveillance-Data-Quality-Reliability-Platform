from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class HeartbeatCreate(BaseModel):
    camera_id: str = Field(..., description="The ID of the camera sending the heartbeat")
    status: str = Field("ok", description="Status reported by the camera (ok, degraded, error)")
    latency_ms: int = Field(0, description="Transmission latency in milliseconds")
    timestamp: datetime | None = Field(
        None, description="Optional timestamp of heartbeat. Defaults to server time if missing."
    )


class HeartbeatResponse(BaseModel):
    id: uuid.UUID
    camera_id: str
    timestamp: datetime
    status: str
    latency_ms: int

    class Config:
        from_attributes = True
