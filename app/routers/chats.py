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

@router.get("/meta/konusmalarim")
async def get_konusmalar(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Kullanıcının mesajlaştığı kişileri döndür"""
    from sqlalchemy import or_
    result = await db.execute(
        select(models.Chat).where(
            or_(
                models.Chat.sender_id == current_user.id,
                models.Chat.receiver_id == current_user.id
            )
        ).order_by(models.Chat.created_at.desc())
    )
    mesajlar = result.scalars().all()
    
    # Benzersiz kişileri bul
    kisi_ids = set()
    for m in mesajlar:
        if m.sender_id != current_user.id:
            kisi_ids.add(m.sender_id)
        if m.receiver_id != current_user.id:
            kisi_ids.add(m.receiver_id)
    
    if not kisi_ids:
        return []
    
    result2 = await db.execute(
        select(models.User).where(models.User.id.in_(kisi_ids))
    )
    users = result2.scalars().all()
    
    # Son mesajı da ekle
    kisiler = []
    for u in users:
        son_mesaj = next((m for m in mesajlar if m.sender_id == u.id or m.receiver_id == u.id), None)
        kisiler.append({
            "id": u.id,
            "isim": u.isim,
            "rol": u.rol,
            "son_mesaj": son_mesaj.mesaj if son_mesaj else "",
            "son_tarih": str(son_mesaj.created_at) if son_mesaj else ""
        })
    
    return kisiler

@router.get("/meta/okunmamis-sayisi")
async def okunmamis_mesaj_sayisi(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    from sqlalchemy import func
    result = await db.execute(
        select(func.count(models.Chat.id)).where(
            models.Chat.receiver_id == current_user.id,
            models.Chat.okundu == False
        )
    )
    sayi = result.scalar()
    return {"sayi": sayi or 0}

@router.patch("/{user2_id}/okundu")
async def mesajlari_okundu_yap(
    user2_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    result = await db.execute(
        select(models.Chat).where(
            models.Chat.sender_id == user2_id,
            models.Chat.receiver_id == current_user.id,
            models.Chat.okundu == False
        )
    )
    mesajlar = result.scalars().all()
    for m in mesajlar:
        m.okundu = True
    await db.commit()
    return {"guncellenen": len(mesajlar)}
