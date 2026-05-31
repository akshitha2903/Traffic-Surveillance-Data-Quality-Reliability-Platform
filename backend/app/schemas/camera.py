from datetime import datetime
from pydantic import BaseModel, Field


class CameraBase(BaseModel):
    id: str = Field(..., description="Unique string identifier for the camera, e.g. cam-01")
    name: str = Field(..., description="Human-readable name of the camera location")
    location: str = Field(..., description="General location or intersection name")
    status: str = Field("active", description="Current status of the camera (active, offline, degraded)")
    is_active: bool = Field(True, description="Whether the camera is active")


class CameraCreate(CameraBase):
    pass


class CameraUpdate(BaseModel):
    name: str | None = None
    location: str | None = None
    status: str | None = None
    is_active: bool | None = None


class CameraResponse(CameraBase):
    last_heartbeat: datetime | None = None
    created_at: datetime

    class Config:
        from_attributes = True
