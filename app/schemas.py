from pydantic import BaseModel, EmailStr

# 1. Kullanıcı Oluşturulurken İstenen Veriler (Frontend -> Backend)
class UserCreate(BaseModel):
    isim: str
    email: EmailStr  # Email formatında olup olmadığını kontrol eder
    sifre: str

# 2. Kullanıcı Oluşturulduktan Sonra Geri Dönen Veriler (Backend -> Frontend)
# (Şifreyi geri döndürmüyoruz, güvenlik kuralı!)
class UserResponse(BaseModel):
    id: int
    isim: str
    email: EmailStr
    # created_at: datetime  # İstersen bunu da ekleyebilirsin ama şimdilik gerek yok

    class Config:
        # Bu ayar, veritabanı modelini (SQLAlchemy) Pydantic modeline dönüştürmeyi sağlar
        from_attributes = True