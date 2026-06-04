from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.hashing import verify_password, hash_password
from app.utils.auth_token import create_access_token
from pydantic import BaseModel, EmailStr
import os
import httpx
from dotenv import load_dotenv
import random
from datetime import datetime, timedelta

load_dotenv()

router = APIRouter(prefix="/auth", tags=["Auth"])

class SifreSifirlaSchema(BaseModel):
    email: EmailStr
    kod: str
    yeni_sifre: str

# ---- MAIL SENDING FUNCTION ----
async def send_email(to: str, subject: str, html: str):
    try:
        api_key = os.getenv("BREVO_API_KEY")
        payload = {
            "sender": {"name": os.getenv("MAIL_FROM_NAME"), "email": os.getenv("MAIL_FROM")},
            "to": [{"email": to}],
            "subject": subject,
            "htmlContent": html
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                json=payload,
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json"
                }
            )
        if response.status_code not in [200, 201]:
            print(f"❌ Brevo API hatası: {response.text}")
            raise Exception(f"Brevo API hatası: {response.status_code}")
        print(f"✅ Email başarıyla gönderildi: {to}")
    except Exception as e:
        print(f"❌ Email gönderim hatası: {e}")
        raise HTTPException(status_code=500, detail="E-posta gönderilirken bir hata oluştu.")

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
        "id": existing_user.id,
        "isim": existing_user.isim,
        "rol": existing_user.rol
    }

# ---- RESET PASSWORD REQUEST ----
@router.post("/sifre-sifirla-talep")
async def sifre_sifirla_talep(email: EmailStr, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).where(models.User.email == email))
    user = result.scalar_one_or_none()

    if user:
        kod = str(random.randint(100000, 999999))
        user.reset_token = kod
        user.reset_token_expire = datetime.utcnow() + timedelta(minutes=10)
        await db.commit()

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #070b14; color: white; padding: 20px;">
            <div style="max-width: 500px; margin: auto; background: #0f172a; padding: 30px; border-radius: 12px; text-align: center; border: 1px solid #1e293b;">
                <h2 style="color: #3b82f6; margin-bottom: 20px;">SafeKampus Şifre Sıfırlama</h2>
                <p style="font-size: 16px; color: #cbd5e1;">Merhaba {user.isim},</p>
                <p style="color: #94a3b8;">Hesap şifrenizi sıfırlamak için doğrulama kodunuz aşağıdadır:</p>
                <div style="background: #1e293b; color: #3b82f6; font-size: 32px; font-weight: bold; letter-spacing: 5px; padding: 15px; margin: 20px 0; border-radius: 8px; border: 1px solid #3b82f6;">
                    {kod}
                </div>
                <p style="font-size: 13px; color: #64748b;">Bu kod 10 dakika süreyle geçerlidir.</p>
                <p style="font-size: 12px; color: #475569; margin-top: 30px;">Eğer bu isteği siz yapmadıysanız, bu e-postayı güvenle göz ardı edebilirsiniz.</p>
            </div>
        </body>
        </html>
        """
        await send_email(email, "SafeKampus - Şifre Sıfırlama Doğrulama Kodu", html)

    return {"mesaj": "Eğer e-posta adresi sistemde kayıtlıysa, 6 haneli sıfırlama kodu gönderildi."}

# ---- RESET PASSWORD ----
@router.post("/sifre-sifirla")
async def sifre_sifirla(data: SifreSifirlaSchema, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.User).where(
            models.User.email == data.email,
            models.User.reset_token == data.kod,
            models.User.reset_token_expire > datetime.utcnow()
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=400, detail="Girdiğiniz kod geçersiz veya süresi dolmuş.")

    user.sifre = hash_password(data.yeni_sifre)
    user.reset_token = None
    user.reset_token_expire = None
    await db.commit()

    return {"mesaj": "Şifreniz başarıyla güncellendi. Yeni şifrenizle giriş yapabilirsiniz."}