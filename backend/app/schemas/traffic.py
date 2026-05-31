from datetime import datetime
import uuid
from pydantic import BaseModel, Field


class TrafficDataCreate(BaseModel):
    camera_id: str = Field(..., description="The ID of the camera reporting telemetry")
    vehicle_count: int = Field(..., ge=0, description="Count of vehicles in this interval")
    average_speed: float = Field(..., ge=0.0, description="Average speed of vehicles in km/h")
    timestamp: datetime | None = Field(
        None, description="Optional timestamp of count. Defaults to server time if missing."
    )


class TrafficDataResponse(BaseModel):
    id: uuid.UUID
    camera_id: str
    timestamp: datetime
    vehicle_count: int
    average_speed: float
    anomalous: bool
    anomaly_reason: str | None

    class Config:
        from_attributes = True
