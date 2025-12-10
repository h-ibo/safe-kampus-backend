from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base

# Şimdilik router (users, events) eklemiyoruz, sadece altyapıyı kuruyoruz.

# Veritabanı tablolarını oluşturacak fonksiyon
async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Uygulamayı başlat
app = FastAPI(title="SafeKampus API", on_startup=[init_models])

# CORS Ayarları (Mobil bağlantı için şart)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "SafeKampus API - Şablon Hazır!"}