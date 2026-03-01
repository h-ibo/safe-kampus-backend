from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/chats",
    tags=["Sohbet"]
)

@router.post("/")
async def send_message(mesaj: schemas.ChatCreate, db: AsyncSession = Depends(get_db)):
    yeni_mesaj = models.Chat(
        sender_id=mesaj.sender_id,
        receiver_id=mesaj.receiver_id,
        mesaj=mesaj.mesaj
    )
    db.add(yeni_mesaj)
    await db.commit()
    await db.refresh(yeni_mesaj)
    return yeni_mesaj

@router.get("/{user1_id}/{user2_id}")
async def get_messages(user1_id: int, user2_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Chat).where(
            or_(
                and_(models.Chat.sender_id == user1_id, models.Chat.receiver_id == user2_id),
                and_(models.Chat.sender_id == user2_id, models.Chat.receiver_id == user1_id)
            )
        ).order_by(models.Chat.created_at)
    )
    return result.scalars().all()