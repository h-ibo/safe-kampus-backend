from pydantic import BaseModel, EmailStr

# 1. Kullanıcı Oluşturulurken İstenen Veriler (Frontend -> Backend)
class UserCreate(BaseModel):
    isim: str
    email: EmailStr
    sifre: str
    rol: str = "ogrenci"  # varsayılan ogrenci

# 2. Kullanıcı Oluşturulduktan Sonra Geri Dönen Veriler (Backend -> Frontend)
# (Şifreyi geri döndürmüyoruz, güvenlik kuralı!)
class UserResponse(BaseModel):
    id: int
    isim: str
    email: EmailStr
    rol: str

    class Config:
        from_attributes = True



class OlayCreate(BaseModel):
    olay_turu: str
    konum: str
    aciklama: str = None
    latitude: float = None
    longitude: float = None

# 4. Duyuru Oluşturulurken İstenen Veriler
class AnnouncementCreate(BaseModel):
    baslik: str
    icerik: str

# 5. Bildirim Oluşturulurken İstenen Veriler
class NotificationCreate(BaseModel):
    user_id: int
    mesaj: str

# 6. Harita Konumu Oluşturulurken İstenen Veriler
class MapLocationCreate(BaseModel):
    isim: str
    latitude: float
    longitude: float
    aciklama: str = None

# 7. Güvenlik Personeli Oluşturulurken İstenen Veriler
class SecurityStaffCreate(BaseModel):
    isim: str
    email: EmailStr
    sifre: str
    telefon: str = None

# 8. Sohbet Mesajı Oluşturulurken İstenen Veriler
class ChatCreate(BaseModel):
    sender_id: int
    receiver_id: int
    mesaj: str
# Login için ayrı schema
class UserLogin(BaseModel):
    email: EmailStr
    sifre: str
