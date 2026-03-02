from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.hashing import verify_password
from app.utils.token import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.User).where(models.User.email == form_data.username)
    )
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=400, detail="Email kayıtlı değil.")
    
    if not verify_password(form_data.password, existing_user.sifre):
        raise HTTPException(status_code=400, detail="Şifre yanlış.")

    token = create_access_token({"user_id": existing_user.id})
    return {"access_token": token, "token_type": "bearer"}