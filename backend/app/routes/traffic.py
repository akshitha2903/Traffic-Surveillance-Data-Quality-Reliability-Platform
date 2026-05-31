from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.camera import Camera
from app.models.traffic import TrafficData
from app.schemas.traffic import TrafficDataCreate, TrafficDataResponse

router = APIRouter(prefix="/api/traffic", tags=["traffic"])


@router.post("", response_model=TrafficDataResponse, status_code=status.HTTP_201_CREATED)
async def ingest_traffic_data(
    traffic_in: TrafficDataCreate, db: AsyncSession = Depends(get_db)
) -> TrafficData:
    """Ingest camera traffic telemetry (vehicle counts, speed) and perform basic anomaly checks."""
    # 1. Verify camera exists
    result = await db.execute(select(Camera).where(Camera.id == traffic_in.camera_id))
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {traffic_in.camera_id} not found",
        )

    # 2. Determine timestamp
    data_time = traffic_in.timestamp or func.now()

    # 3. Simple threshold anomaly checks (Phase 3 will introduce advanced validation)
    anomalous = False
    anomaly_reason = None

    if traffic_in.vehicle_count > 400:
        anomalous = True
        anomaly_reason = f"Vehicle count ({traffic_in.vehicle_count}) exceeds threshold (400)"
    elif traffic_in.average_speed > 140:
        anomalous = True
        anomaly_reason = f"Average speed ({traffic_in.average_speed} km/h) exceeds safe limits"
    elif traffic_in.vehicle_count < 0:
        anomalous = True
        anomaly_reason = "Negative vehicle count reported"

    # 4. Save the traffic record
    db_traffic = TrafficData(
        camera_id=camera.id,
        timestamp=data_time,
        vehicle_count=traffic_in.vehicle_count,
        average_speed=traffic_in.average_speed,
        anomalous=anomalous,
        anomaly_reason=anomaly_reason,
    )
    db.add(db_traffic)
    await db.commit()
    await db.refresh(db_traffic)
    return db_traffic
