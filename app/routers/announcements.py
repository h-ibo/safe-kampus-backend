from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.dependencies import get_current_user
from app.utils.dependencies import get_current_user, require_admin

router = APIRouter(
    prefix="/announcements",
    tags=["Duyurular"]
)

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
    return yeni_duyuru

@router.get("/")
async def get_announcements(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(select(models.Announcement))
    return result.scalars().all()