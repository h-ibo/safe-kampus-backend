from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.dependencies import get_current_user, require_admin
from app.utils.push import send_push_to_all

router = APIRouter(prefix="/announcements", tags=["Duyurular"])

@router.post("/")
async def create_announcement(
    duyuru: schemas.AnnouncementCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    yeni_duyuru = models.Announcement(
        baslik=duyuru.baslik,
        icerik=duyuru.icerik
    )
    db.add(yeni_duyuru)
    await db.commit()
    await db.refresh(yeni_duyuru)

    # Herkese bildirim gönder
    await send_push_to_all(db, f"📢 {duyuru.baslik}", duyuru.icerik, {"duyuru_id": yeni_duyuru.id})

    return yeni_duyuru

@router.get("/")
async def get_announcements(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    sayfa: int = 1,
    limit: int = 10
):
    offset = (sayfa - 1) * limit
    result = await db.execute(
        select(models.Announcement).offset(offset).limit(limit)
    )
    return result.scalars().all()
