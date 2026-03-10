from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.hashing import verify_password, hash_password
from app.utils.token import create_access_token
from pydantic import EmailStr
import os
from dotenv import load_dotenv
import secrets
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

# ---- MAIL SENDING FUNCTION ----
async def send_email(to: str, subject: str, html: str):
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = os.getenv("MAIL_FROM")
        msg["To"] = to
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname="smtp.gmail.com",
            port=465,
            username=os.getenv("MAIL_USERNAME"),
            password=os.getenv("MAIL_PASSWORD"),
            use_tls=True,
        )
        print(f"✅ Email gönderildi: {to}")
    except Exception as e:
        print(f"❌ Email hatası: {e}")
        raise e

# ---- LOGIN ----
@router.post("/login")
async def login(user: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(models.User.email == user.email)
    )
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code=400, detail="Email kayıtlı değil.")

    if not verify_password(user.sifre, existing_user.sifre):
        raise HTTPException(status_code=400, detail="Şifre yanlış.")

    token = create_access_token({"user_id": existing_user.id})

    return {
        "access_token": token,
        "token_type": "bearer",
        "isim": existing_user.isim,
        "rol": existing_user.rol
    }

# ---- RESET PASSWORD REQUEST ----
@router.post("/sifre-sifirla-talep")
async def sifre_sifirla_talep(email: EmailStr, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # 1 saat geçerli token oluştur
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expire = datetime.utcnow() + timedelta(hours=1)
        await db.commit()

        reset_link = f"http://localhost:8081/sifre-sifirla?token={token}"
        html = f"""
        <h2>Şifre Sıfırlama</h2>
        <p>Merhaba {user.isim},</p>
        <p>Şifrenizi sıfırlamak için aşağıdaki linke tıklayın:</p>
        <a href="{reset_link}" style="background:#1a56db;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;display:inline-block;margin:16px 0;">
            Şifremi Sıfırla
        </a>
        <p>Bu link 1 saat geçerlidir.</p>
        <p>Eğer bu isteği siz yapmadıysanız bu emaili görmezden gelin.</p>
        <br><p>SafeKampus Güvenlik Sistemi</p>
        """
        await send_email(email, "SafeKampus - Şifre Sıfırlama", html)

    return {"mesaj": "Eğer bu email kayıtlıysa sıfırlama linki gönderildi."}

# ---- RESET PASSWORD ----
@router.post("/sifre-sifirla")
async def sifre_sifirla(token: str, yeni_sifre: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(
            models.User.reset_token == token,
            models.User.reset_token_expire > datetime.utcnow()
        )
    )
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Geçersiz veya süresi dolmuş token.")

    # Şifreyi güncelle ve reset alanlarını temizle
    user.sifre = hash_password(yeni_sifre)
    user.reset_token = None
    user.reset_token_expire = None
    await db.commit()

    return {"mesaj": "Şifre başarıyla güncellendi."}