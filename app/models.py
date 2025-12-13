from sqlalchemy import Column, Integer, String, Text, TIMESTAMP
from .database import Base
from datetime import datetime

# 1. KULLANICI TABLOSU 
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    isim = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    sifre = Column(String(150), nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 2. OLAYLAR TABLOSU 
class Olay(Base):
    __tablename__ = "olaylar"

    id = Column(Integer, primary_key=True, index=True)
    olay_turu = Column(String(100), nullable=False)
    konum = Column(String(150), nullable=False)
    aciklama = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)