from exponent_server_sdk import PushClient, PushMessage, PushServerError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models

async def save_notification(db: AsyncSession, user_id: int, mesaj: str):
    """Veritabanına bildirim kaydet"""
    bildirim = models.Notification(user_id=user_id, mesaj=mesaj)
    db.add(bildirim)
    await db.flush()

async def send_push_to_users(db: AsyncSession, user_ids: list, title: str, body: str, data: dict = {}):
    result = await db.execute(
        select(models.User).where(models.User.id.in_(user_ids))
    )
    users = result.scalars().all()
    
    for user in users:
        await save_notification(db, user.id, f"{title}: {body}")
    
    await db.commit()
    
    tokens = [u.push_token for u in users if u.push_token]
    await send_push_notifications(tokens, title, body, data)

async def send_push_to_role(db: AsyncSession, rol: str, title: str, body: str, data: dict = {}):
    result = await db.execute(
        select(models.User).where(models.User.rol == rol)
    )
    users = result.scalars().all()
    
    for user in users:
        await save_notification(db, user.id, f"{title}: {body}")
    
    await db.commit()
    
    tokens = [u.push_token for u in users if u.push_token]
    await send_push_notifications(tokens, title, body, data)

async def send_push_to_all(db: AsyncSession, title: str, body: str, data: dict = {}):
    result = await db.execute(select(models.User))
    users = result.scalars().all()
    
    for user in users:
        await save_notification(db, user.id, f"{title}: {body}")
    
    await db.commit()
    
    tokens = [u.push_token for u in users if u.push_token]
    await send_push_notifications(tokens, title, body, data)

async def send_push_notifications(tokens: list, title: str, body: str, data: dict = {}):
    if not tokens:
        return
    try:
        messages = [
            PushMessage(to=token, title=title, body=body, data=data)
            for token in tokens
        ]
        PushClient().publish_multiple(messages)
        print(f"✅ Push notification gönderildi: {len(tokens)} kullanıcı")
    except PushServerError as e:
        print(f"❌ Push notification hatası: {e}")
    except Exception as e:
        print(f"❌ Push notification hatası: {e}")
