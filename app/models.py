from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Float, ForeignKey, Boolean
from .database import Base
from datetime import datetime

# 1. KULLANICI TABLOSU
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    isim = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    sifre = Column(String(150), nullable=False)
    rol = Column(String(50), default="ogrenci")  # ogrenci, guvenlik, admin
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    rol = Column(String(50), default="ogrenci")
    telefon = Column(String(20), nullable=True)

# 2. OLAYLAR TABLOSU
class Olay(Base):
    __tablename__ = "olaylar"

    id = Column(Integer, primary_key=True, index=True)
    olay_turu = Column(String(100), nullable=False)
    konum = Column(String(150), nullable=False)
    aciklama = Column(Text)
    durum = Column(String(50), default="beklemede")  # beklemede, inceleniyor, cozuldu
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 3. GÜVENLİK PERSONELİ TABLOSU
class SecurityStaff(Base):
    __tablename__ = "security_staff"

    id = Column(Integer, primary_key=True, index=True)
    isim = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    sifre = Column(String(150), nullable=False)
    telefon = Column(String(20))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 4. DUYURULAR TABLOSU
class Announcement(Base):
    __tablename__ = "announcements"

    id = Column(Integer, primary_key=True, index=True)
    baslik = Column(String(150), nullable=False)
    icerik = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 5. BİLDİRİMLER TABLOSU
class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mesaj = Column(Text, nullable=False)
    okundu = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 6. SOHBET TABLOSU
class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    mesaj = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

# 7. HARİTA KONUMLARI TABLOSU
class MapLocation(Base):
    __tablename__ = "map_locations"

    id = Column(Integer, primary_key=True, index=True)
    isim = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    aciklama = Column(Text)