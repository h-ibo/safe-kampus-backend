from exponent_server_sdk import PushClient, PushMessage, PushServerError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import models

async def send_push_to_users(db: AsyncSession, user_ids: list, title: str, body: str, data: dict = {}):
    """Belirli kullanıcılara push notification gönder"""
    result = await db.execute(
        select(models.User).where(
            models.User.id.in_(user_ids),
            models.User.push_token != None
        )
    )
    users = result.scalars().all()
    
    tokens = [u.push_token for u in users if u.push_token]
    await send_push_notifications(tokens, title, body, data)

async def send_push_to_role(db: AsyncSession, rol: str, title: str, body: str, data: dict = {}):
    """Belirli roldeki tüm kullanıcılara push notification gönder"""
    result = await db.execute(
        select(models.User).where(
            models.User.rol == rol,
            models.User.push_token != None
        )
    )
    users = result.scalars().all()
    
    tokens = [u.push_token for u in users if u.push_token]
    await send_push_notifications(tokens, title, body, data)

async def send_push_to_all(db: AsyncSession, title: str, body: str, data: dict = {}):
    """Tüm kullanıcılara push notification gönder"""
    result = await db.execute(
        select(models.User).where(models.User.push_token != None)
    )
    users = result.scalars().all()
    
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
