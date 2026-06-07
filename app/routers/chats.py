from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from typing import Dict

from app.database import get_db
from app import models, schemas
from app.utils.dependencies import get_current_user
from app.utils.push import send_push_to_users

router = APIRouter(prefix="/chats", tags=["Sohbet"])

# ---------------------------
# WEBSOCKET MANAGER
# ---------------------------
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: int):
        self.active_connections.pop(user_id, None)

    async def send_personal_message(self, message: dict, user_id: int):
        ws = self.active_connections.get(user_id)
        if ws:
            try:
                await ws.send_json(message)
            except:
                self.disconnect(user_id)

manager = ConnectionManager()

# ---------------------------
# SEND MESSAGE
# ---------------------------
@router.post("/")
async def send_message(
    mesaj: schemas.ChatCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    yeni = models.Chat(
        sender_id=current_user.id,
        receiver_id=mesaj.receiver_id,
        mesaj=mesaj.mesaj,
        image_url=getattr(mesaj, "image_url", None)
    )

    db.add(yeni)
    await db.commit()
    await db.refresh(yeni)

    await send_push_to_users(
        db,
        [mesaj.receiver_id],
        "💬 Yeni Mesaj",
        mesaj.mesaj or "📷 Fotoğraf",
        {"chat": True}
    )

    await manager.send_personal_message(
        {
            "id": yeni.id,
            "sender_id": yeni.sender_id,
            "receiver_id": yeni.receiver_id,
            "mesaj": yeni.mesaj,
            "image_url": yeni.image_url,
            "okundu": yeni.okundu
        },
        mesaj.receiver_id
    )

    return yeni

# ---------------------------
# WS
# ---------------------------
@router.websocket("/ws/{user_id}")
async def ws(websocket: WebSocket, user_id: int):
    await manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(user_id)
# ---------------------------
# GÜVENLİK LİSTESİ
# ---------------------------
@router.get("/guvenlik-listesi")
async def guvenlik_listesi(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(models.User).where(
            or_(models.User.rol == "guvenlik", models.User.rol == "admin")
        )
    )
    return result.scalars().all()

# ---------------------------
# MESAJLARI GETİR
# ---------------------------
@router.get("/{diger_id}")
async def mesajlari_getir(
    diger_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(models.Chat).where(
            or_(
                and_(models.Chat.sender_id == current_user.id, models.Chat.receiver_id == diger_id),
                and_(models.Chat.sender_id == diger_id, models.Chat.receiver_id == current_user.id)
            )
        ).order_by(models.Chat.created_at)
    )
    return result.scalars().all()

# ---------------------------
# OKUNDU İŞARETLE
# ---------------------------
@router.patch("/{diger_id}/okundu")
async def okundu_isle(
    diger_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
    result = await db.execute(
        select(models.Chat).where(
            and_(models.Chat.sender_id == diger_id, models.Chat.receiver_id == current_user.id, models.Chat.okundu == False)
        )
    )
    mesajlar = result.scalars().all()
    for m in mesajlar:
        m.okundu = True
    await db.commit()
    return {"okundu": len(mesajlar)}

# ---------------------------
# KONUŞMALARIM (Güvenlik için)
# ---------------------------
@router.get("/meta/konusmalarim")
async def konusmalarim(
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user)
):
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
        diger = m.receiver_id if m.sender_id == current_user.id else m.sender_id
        kisi_ids.add(diger)
    
    konusmalar = []
    for kisi_id in kisi_ids:
        kisi_result = await db.execute(select(models.User).where(models.User.id == kisi_id))
        kisi = kisi_result.scalar_one_or_none()
        if kisi:
            son_mesaj = next((m.mesaj for m in mesajlar if m.sender_id == kisi_id or m.receiver_id == kisi_id), None)
            konusmalar.append({"id": kisi.id, "isim": kisi.isim, "rol": kisi.rol, "son_mesaj": son_mesaj})
    
    return konusmalar
