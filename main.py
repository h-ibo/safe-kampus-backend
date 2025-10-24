# 1. Gerekli importlar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # CORS için

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