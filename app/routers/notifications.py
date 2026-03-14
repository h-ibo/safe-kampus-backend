from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/notifications",
    tags=["Bildirimler"]
)

@router.post("/")
async def create_notification(
    bildirim: schemas.NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    yeni_bildirim = models.Notification(
        user_id=bildirim.user_id,
        mesaj=bildirim.mesaj
    )
    db.add(yeni_bildirim)
    await db.commit()
    await db.refresh(yeni_bildirim)
    return yeni_bildirim

@router.get("/{user_id}")
async def get_notifications(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Notification).where(models.Notification.user_id == user_id)
    )
    return result.scalars().all()

@router.patch("/{notification_id}/okundu")
async def mark_as_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Notification).where(models.Notification.id == notification_id)
    )
    bildirim = result.scalar_one_or_none()
    if bildirim:
        bildirim.okundu = True
        await db.commit()
        await db.refresh(bildirim)
    return bildirim
@router.get("/meta/okunmamis-sayisi")
async def okunmamis_bildirim_sayisi(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(models.Notification.id)).where(
            models.Notification.user_id == current_user.id,
            models.Notification.okundu == False
        )
    )
    sayi = result.scalar()
    return {"sayi": sayi or 0}

@router.get("/meta/okunmamis-sayisi")
async def okunmamis_bildirim_sayisi(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(models.Notification.id)).where(
            models.Notification.user_id == current_user.id,
            models.Notification.okundu == False
        )
    )
    sayi = result.scalar()
    return {"sayi": sayi or 0}
