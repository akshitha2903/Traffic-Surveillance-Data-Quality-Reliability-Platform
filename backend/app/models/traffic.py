from datetime import datetime
import uuid
from sqlalchemy import String, Integer, Float, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TrafficData(Base):
    __tablename__ = "traffic_data"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    camera_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, server_default=func.now()
    )
    vehicle_count: Mapped[int] = mapped_column(Integer, nullable=False)
    average_speed: Mapped[float] = mapped_column(Float, nullable=False)
    anomalous: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    anomaly_reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
