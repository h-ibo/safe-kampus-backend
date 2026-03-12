from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.database import get_db
from app import models, schemas
from app.utils.dependencies import get_current_user
from app.utils.push import send_push_to_users

router = APIRouter(prefix="/chats", tags=["Sohbet"])

@router.post("/")
async def send_message(
    mesaj: schemas.ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    yeni_mesaj = models.Chat(
        sender_id=current_user.id,
        receiver_id=mesaj.receiver_id,
        mesaj=mesaj.mesaj,
        image_url=mesaj.image_url if hasattr(mesaj, 'image_url') else None
    )
    db.add(yeni_mesaj)
    await db.commit()
    await db.refresh(yeni_mesaj)

    # Alıcıya bildirim gönder
    await send_push_to_users(
        db, [mesaj.receiver_id],
        f"💬 Yeni Mesaj",
        mesaj.mesaj or "📷 Fotoğraf gönderildi",
        {"chat": True}
    )

    return yeni_mesaj

@router.get("/guvenlik-listesi")
async def get_guvenlik_listesi(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Kullanıcının yazışabileceği güvenlik/admin listesi"""
    result = await db.execute(
        select(models.User).where(
            models.User.rol.in_(["admin", "guvenlik"])
        )
    )
    users = result.scalars().all()
    return [{"id": u.id, "isim": u.isim, "rol": u.rol} for u in users]

@router.get("/{user2_id}")
async def get_messages(
    user2_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Chat).where(
            or_(
                and_(models.Chat.sender_id == current_user.id, models.Chat.receiver_id == user2_id),
                and_(models.Chat.sender_id == user2_id, models.Chat.receiver_id == current_user.id)
            )
        ).order_by(models.Chat.created_at)
    )
    return result.scalars().all()

@router.post("/resim-yukle")
async def resim_yukle(
    data: dict,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Base64 resmi kaydet ve URL döndür"""
    import base64, os, uuid
    
    image_data = data.get("image")
    if not image_data:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Resim verisi eksik.")
    
    # Base64 decode
    if "," in image_data:
        image_data = image_data.split(",")[1]
    
    image_bytes = base64.b64decode(image_data)
    filename = f"{uuid.uuid4()}.jpg"
    filepath = f"/tmp/{filename}"
    
    with open(filepath, "wb") as f:
        f.write(image_bytes)
    
    # Railway'de dosya sistemi kalıcı değil, base64 olarak döndür
    return {"image_url": f"data:image/jpeg;base64,{data.get('image').split(',')[-1]}"}
