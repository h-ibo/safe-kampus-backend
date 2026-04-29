from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .database import engine, Base
from .routers import users, olaylar, announcements, notifications, map_locations, security_staff, chats, ai_chat
from app.routers import auth

# 🔥 ENV LOAD (EN ÖNEMLİ SATIR)
load_dotenv()

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(
    title="SafeKampus API",
    swagger_ui_parameters={"persistAuthorization": True}
)

@app.on_event("startup")
async def startup():
    await init_models()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(olaylar.router)
app.include_router(announcements.router)
app.include_router(notifications.router)
app.include_router(map_locations.router)
app.include_router(security_staff.router)
app.include_router(chats.router)
app.include_router(ai_chat.router)

@app.get("/")
async def root():
    return {"message": "SafeKampus API - OK"}