from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.database import get_db
from app.models.camera import Camera
from app.schemas.camera import CameraCreate, CameraResponse, CameraUpdate

router = APIRouter(prefix="/api/cameras", tags=["cameras"])


@router.post("", response_model=CameraResponse, status_code=status.HTTP_201_CREATED)
async def register_camera(
    camera_in: CameraCreate, db: AsyncSession = Depends(get_db)
) -> Camera:
    """Register a new camera or return existing if ID matches."""
    result = await db.execute(select(Camera).where(Camera.id == camera_in.id))
    existing_camera = result.scalar_one_or_none()
    if existing_camera:
        # If camera already exists, let's return it (makes simulator restarts easy)
        return existing_camera

    db_camera = Camera(
        id=camera_in.id,
        name=camera_in.name,
        location=camera_in.location,
        status=camera_in.status,
        is_active=camera_in.is_active,
    )
    db.add(db_camera)
    await db.commit()
    await db.refresh(db_camera)
    return db_camera


@router.get("", response_model=list[CameraResponse])
async def list_cameras(db: AsyncSession = Depends(get_db)) -> list[Camera]:
    """Retrieve all registered cameras."""
    result = await db.execute(select(Camera))
    return list(result.scalars().all())


@router.get("/{camera_id}", response_model=CameraResponse)
async def get_camera(camera_id: str, db: AsyncSession = Depends(get_db)) -> Camera:
    """Get details of a specific camera by ID."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found",
        )
    return camera


@router.patch("/{camera_id}", response_model=CameraResponse)
async def update_camera(
    camera_id: str, camera_in: CameraUpdate, db: AsyncSession = Depends(get_db)
) -> Camera:
    """Update camera details."""
    result = await db.execute(select(Camera).where(Camera.id == camera_id))
    camera = result.scalar_one_or_none()
    if not camera:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Camera with ID {camera_id} not found",
        )

    update_data = camera_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(camera, field, value)

    await db.commit()
    await db.refresh(camera)
    return camera
