from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.hashing import hash_password
from app.utils.dependencies import get_current_user

router = APIRouter(
    prefix="/security-staff",
    tags=["Güvenlik Personeli"]
)

@router.post("/")
async def create_security_staff(
    personel: schemas.SecurityStaffCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(models.SecurityStaff).where(models.SecurityStaff.email == personel.email)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")
    
    yeni_personel = models.SecurityStaff(
        isim=personel.isim,
        email=personel.email,
        sifre=hash_password(personel.sifre),
        telefon=personel.telefon
    )
    db.add(yeni_personel)
    await db.commit()
    await db.refresh(yeni_personel)
    return yeni_personel

@router.get("/")
async def get_security_staff(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(select(models.SecurityStaff))
    return result.scalars().all()