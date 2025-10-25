# 1. Gerekli importlar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # CORS için
from pydantic import BaseModel
from sqlalchemy import text
from database import SessionLocal

# 2. FastAPI uygulamasını oluştur
app = FastAPI()

# --- CORS AYARLARI ---
# İzin verilecek frontend adreslerinin listesi
origins = [
    "http://localhost:5173", # Vite adresi (isteğe bağlı, kalabilir)
    "http://localhost:8081", # Expo Web genellikle bu portu kullanır <<< YENİ EKLENDİ
    "http://127.0.0.1:8081", # Bazen localhost yerine IP kullanılır <<< YENİ EKLENDİ
    # Gelecekte Expo Go (mobil) için bilgisayarının IP'sini de ekleyebilirsin
    # Örn: "http://192.168.1.5:8081" 
]

# CORS middleware'ini uygulamaya ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # Listemizdeki adreslere izin ver
    allow_credentials=True,    # Kimlik bilgisi (örn: cookie) gönderimine izin ver
    allow_methods=["*"],       # Tüm HTTP metotlarına (GET, POST vb.) izin ver
    allow_headers=["*"],       # Tüm HTTP başlıklarına izin ver
)
# --- CORS AYARLARI BİTTİ ---


# 4. Endpoint tanımları (Aynı kaldı)
@app.get("/")
async def read_root():
    return {"message": "Safe Kampüs Backend Çalışıyor! (CORS Güncellendi)"} # Mesajı güncelledik

@app.get("/api/test")
async def test_endpoint():
    return {"status": "success", "data": "Bu bir test verisidir. (Backend'den geldi)"} # Mesajı güncelledik

# 5. Sunucuyu çalıştırmak için terminalde: uvicorn main:app --reload
@app.get("/merhaba/{isim}")

async def merhaba_de(isim:str):
    return {"mesaj:"f"Merhaba {isim},fastapini gotune koyim"}

@app.get("/ogeler/")

async def ogeleri_oku(skip: int=0,limit: int=10):
    tum_ogeler = [f"Öğe {i}"for i in range(100)]
    gosterilecek_ogeler = tum_ogeler[skip : skip + limit]

    return {"atlanan_oge_sayisi": skip, "gosterilen_oge_sayisi": limit, "ogeler": gosterilecek_ogeler}


class OlayBildirimi(BaseModel):
    Olay_turu:str
    konum:str
    aciklama:str | None=None

@app.post("/Olaylar/")

async def olay_bildir(bildirim:OlayBildirimi):
    print(f"---Olay bildirimi alıdnı")
    print(f"Olay türü : {bildirim.Olay_turu}")
    print(f"konum: {bildirim.konum}")

    if bildirim.aciklama:
        print(f"Açıklama: {bildirim.aciklama}")
    else:
        print("Açıklama: Yok")
    print("---------------------------------")


    return {"status": "success", "message": f"'{bildirim.Olay_turu}' tipindeki olay bildirimi alındı."}

@app.get("/db-test")
async def test_db():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))  # text() ile sarmaladık
        return {"status": "success", "message": "PostgreSQL bağlantısı başarılı!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        db.close()