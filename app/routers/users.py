from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app import models, schemas
from app.utils.hashing import hash_password   # Hashing eklendi

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/", response_model=schemas.UserResponse)
async def create_user(
    user: schemas.UserCreate,
    db: AsyncSession = Depends(get_db)
):

    # Email kontrolü
    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")

    # Şifre HASHLENİYOR
    hashed_password = hash_password(user.sifre)

    new_user = models.User(
    isim=user.isim,
    email=user.email,
    sifre=hashed_password,
    rol=user.rol
)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
from app.utils.dependencies import get_current_user
from app.utils.hashing import hash_password, verify_password

@router.put("/sifre-guncelle")
async def update_password(
    eski_sifre: str,
    yeni_sifre: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if not verify_password(eski_sifre, current_user.sifre):
        raise HTTPException(status_code=400, detail="Eski şifre yanlış.")
    
    current_user.sifre = hash_password(yeni_sifre)
    await db.commit()
    return {"mesaj": "Şifre başarıyla güncellendi."}
@router.put("/profil-guncelle")
async def update_profile(
    isim: str = None,
    telefon: str = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if isim:
        current_user.isim = isim
    if telefon:
        current_user.telefon = telefon
    await db.commit()
    return {"mesaj": "Profil başarıyla güncellendi."}
from app.utils.dependencies import require_admin

@router.get("/", response_model=list[schemas.UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_admin)
):
    result = await db.execute(select(models.User))
    return result.scalars().all()

@router.put("/push-token")
async def push_token_guncelle(
    data: dict,
    current_user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    current_user.push_token = data.get("push_token")
    await db.commit()
    return {"mesaj": "Push token güncellendi."}
