# 1. FastAPI sınıfına EK OLARAK CORSMiddleware'i import et
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # <<< YENİ İMPORT

# 2. Bir FastAPI uygulaması örneği oluştur (Bu satır aynı)
app = FastAPI()

# --- YENİ BÖLÜM: CORS AYARLARI ---
# İzin verilecek frontend adreslerinin listesi
# Geliştirme sırasında React/Vite genellikle 5173 portunu kullanır
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173", # Bazen localhost yerine bu IP kullanılır
    # Eğer React başka port kullanıyorsa onu da ekle (örn: "http://localhost:3000")
]

# CORS middleware'ini uygulamaya ekle
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # Hangi adreslerden gelen isteklere izin verilecek
    allow_credentials=True, # Çerezlere (cookie) izin verilsin mi (ileride gerekebilir)
    allow_methods=["*"],    # Hangi HTTP metotlarına izin verilecek (GET, POST, vb. hepsi)
    allow_headers=["*"],    # Hangi HTTP başlıklarına izin verilecek (hepsi)
)
# --- CORS AYARLARI BİTTİ ---


# 3. Endpoint tanımları (Bu kısımlar aynı kaldı)
@app.get("/")
async def read_root():
    return {"message": "Safe Kampüs Backend Çalışıyor!"}

@app.get("/api/test")
async def test_endpoint():
    return {"status": "success", "data": "Bu bir test verisidir."}

# 4. Sunucuyu çalıştırmak için terminalde şu komutu kullanacağız:
#    uvicorn main:app --reload