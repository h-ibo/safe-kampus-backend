from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database import SessionLocal
from app import models, schemas

# İŞTE BURASI EKSİK OLABİLİR:
router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

async def get_db():
    async with SessionLocal() as db:
        yield db

@router.post("/", response_model=schemas.UserResponse)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == user.email))
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Bu email zaten kayıtlı.")

    new_user = models.User(
        isim=user.isim,
        email=user.email,
        sifre=user.sifre 
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user