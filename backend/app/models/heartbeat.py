from datetime import datetime
import uuid
from sqlalchemy import String, Integer, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Heartbeat(Base):
    __tablename__ = "heartbeats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    camera_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cameras.id", ondelete="CASCADE"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), primary_key=True, server_default=func.now()
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)  # ok, degraded, error
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
