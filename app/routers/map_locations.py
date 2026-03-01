from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/map-locations",
    tags=["Harita Konumları"]
)

@router.post("/")
async def create_location(konum: schemas.MapLocationCreate, db: AsyncSession = Depends(get_db)):
    yeni_konum = models.MapLocation(
        isim=konum.isim,
        latitude=konum.latitude,
        longitude=konum.longitude,
        aciklama=konum.aciklama
    )
    db.add(yeni_konum)
    await db.commit()
    await db.refresh(yeni_konum)
    return yeni_konum

@router.get("/")
async def get_locations(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.MapLocation))
    return result.scalars().all()

@router.delete("/{location_id}")
async def delete_location(location_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.MapLocation).where(models.MapLocation.id == location_id)
    )
    konum = result.scalar_one_or_none()
    if konum:
        await db.delete(konum)
        await db.commit()
    return {"mesaj": "Konum silindi"}