from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/olaylar",
    tags=["Olaylar"]
)

@router.post("/")
async def create_olay(olay: schemas.OlayCreate, db: AsyncSession = Depends(get_db)):
    yeni_olay = models.Olay(
        olay_turu=olay.olay_turu,
        konum=olay.konum,
        aciklama=olay.aciklama
    )
    db.add(yeni_olay)
    await db.commit()
    await db.refresh(yeni_olay)
    return yeni_olay

@router.get("/")
async def get_olaylar(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Olay))
    return result.scalars().all()