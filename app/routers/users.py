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
        sifre=hashed_password
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user
