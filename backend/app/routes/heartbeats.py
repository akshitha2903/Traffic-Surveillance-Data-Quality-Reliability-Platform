from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.camera import Camera
from app.models.heartbeat import Heartbeat
from app.models.status_log import CameraStatusLog
from app.schemas.heartbeat import HeartbeatCreate, HeartbeatResponse

router = APIRouter(prefix="/api/heartbeats", tags=["heartbeats"])


@router.post("", response_model=HeartbeatResponse, status_code=status.HTTP_201_CREATED)
async def ingest_heartbeat(
    heartbeat_in: HeartbeatCreate, db: AsyncSession = Depends(get_db)
) -> Heartbeat:
    """Ingest camera heartbeat and update camera status, logging status changes if any."""
    # 1. Verify camera exists
    result = await db.execute(select(Camera).where(Camera.id == heartbeat_in.camera_id))
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {heartbeat_in.camera_id} not found",
        )

    # 2. Determine timestamps
    heartbeat_time = heartbeat_in.timestamp or func.now()

    # 3. Check for status transition
    # We map "ok" heartbeat status to "active" camera status, and "error"/"degraded" directly
    target_camera_status = "active" if heartbeat_in.status == "ok" else heartbeat_in.status
    
    if camera.status != target_camera_status:
        # Create a status transition log
        status_log = CameraStatusLog(
            camera_id=camera.id,
            timestamp=heartbeat_time,
            from_status=camera.status,
            to_status=target_camera_status,
            reason=f"Status update from ingest endpoint: {heartbeat_in.status}",
        )
        db.add(status_log)
        
        # Update camera status
        camera.status = target_camera_status

    # 4. Update camera last heartbeat time
    camera.last_heartbeat = heartbeat_time

    # 5. Save the heartbeat record
    db_heartbeat = Heartbeat(
        camera_id=camera.id,
        timestamp=heartbeat_time,
        status=heartbeat_in.status,
        latency_ms=heartbeat_in.latency_ms,
    )
    db.add(db_heartbeat)

    await db.commit()
    await db.refresh(db_heartbeat)
    return db_heartbeat
