from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app import models, schemas
from app.utils.dependencies import get_current_user, require_guvenlik
from app.utils.push import send_push_to_role, send_push_to_users

router = APIRouter(prefix="/olaylar", tags=["Olaylar"])

@router.post("/")
async def create_olay(
    olay: schemas.OlayCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    yeni_olay = models.Olay(
        user_id=current_user.id,
        olay_turu=olay.olay_turu,
        konum=olay.konum,
        aciklama=olay.aciklama,
        latitude=olay.latitude,
        longitude=olay.longitude
    )
    db.add(yeni_olay)
    await db.commit()
    await db.refresh(yeni_olay)

    # Admin ve güvenliğe bildirim gönder
    if olay.olay_turu == "ACİL YARDIM":
        await send_push_to_role(db, "admin", "🚨 ACİL YARDIM!", f"{current_user.isim} acil yardım istiyor! Konum: {olay.konum}", {"olay_id": yeni_olay.id})
        await send_push_to_role(db, "guvenlik", "🚨 ACİL YARDIM!", f"{current_user.isim} acil yardım istiyor! Konum: {olay.konum}", {"olay_id": yeni_olay.id})
    else:
        await send_push_to_role(db, "admin", "📢 Yeni Olay", f"{olay.olay_turu} - {olay.konum}", {"olay_id": yeni_olay.id})
        await send_push_to_role(db, "guvenlik", "📢 Yeni Olay", f"{olay.olay_turu} - {olay.konum}", {"olay_id": yeni_olay.id})

    return yeni_olay

@router.get("/")
async def get_olaylar(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    if current_user.rol in ["admin", "guvenlik"]:
        query = select(models.Olay)
    else:
        query = select(models.Olay).where(models.Olay.user_id == current_user.id)
    
    result = await db.execute(query.order_by(models.Olay.created_at.desc()))
    return result.scalars().all()

@router.delete("/{olay_id}")
async def delete_olay(
    olay_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_guvenlik)
):
    result = await db.execute(select(models.Olay).where(models.Olay.id == olay_id))
    olay = result.scalar_one_or_none()
    if olay:
        await db.delete(olay)
        await db.commit()
    return {"mesaj": "Olay silindi"}

@router.put("/{olay_id}/durum")
async def update_olay_durum(
    olay_id: int,
    durum: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(require_guvenlik)
):
    result = await db.execute(select(models.Olay).where(models.Olay.id == olay_id))
    olay = result.scalar_one_or_none()
    if not olay:
        raise HTTPException(status_code=404, detail="Olay bulunamadı.")
    if durum not in ["beklemede", "inceleniyor", "cozuldu"]:
        raise HTTPException(status_code=400, detail="Geçersiz durum.")
    olay.durum = durum
    await db.commit()

    # Kullanıcıya bildirim gönder
    durum_emoji = {"beklemede": "⏳", "inceleniyor": "🔍", "cozuldu": "✅"}
    await send_push_to_users(db, [olay.user_id], 
        f"{durum_emoji.get(durum, '')} Olay Güncellendi",
        f"Olayınızın durumu '{durum}' olarak güncellendi.",
        {"olay_id": olay.id}
    )

    return {"mesaj": f"Olay durumu '{durum}' olarak güncellendi."}
