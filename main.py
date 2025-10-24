# 1. FastAPI sınıfını içeri aktar
from fastapi import FastAPI

# 2. Bir FastAPI uygulaması örneği (nesnesi) oluştur
app = FastAPI()

# 3. Ana sayfa ("/") için bir GET endpoint'i tanımla
@app.get("/")
async def read_root():
    # Tarayıcıya JSON formatında bir mesaj döndür
    return {"message": "Safe Kampüs Backend Çalışıyor!"}

# 4. API testi için başka bir GET endpoint'i tanımla ("/api/test")
@app.get("/api/test")
async def test_endpoint():
    # Başka bir JSON mesajı döndür
    return {"status": "success", "data": "Bu bir test verisidir."}

# 5. Sunucuyu çalıştırmak için terminalde şu komutu kullanacağız:
#    uvicorn main:app --reload