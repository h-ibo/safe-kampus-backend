import sys
import os
import time
import requests

# ---------------------------------------------------------
# 1. YOL AYARI (PYTHONPATH)
# ---------------------------------------------------------
# Bu kısım 'app' klasörünü bulamama hatasını kökten çözer.
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# ---------------------------------------------------------
# 2. MODÜL İMPORTLARI
# ---------------------------------------------------------
try:
    # faiss_store dosyanın nerede olduğunu otomatik bulmaya çalışır
    try:
        from app.utils.faiss_store import chunk_text, add_documents
    except ImportError:
        from app.rag.faiss_store import chunk_text, add_documents
        
    from app.utils.firecrawl import FIRECRAWL_API_KEY
    print("✅ Tüm modüller başarıyla yüklendi.")
except ImportError as e:
    print(f"❌ Kritik Hata: Modüller bulunamadı! Detay: {e}")
    sys.exit(1)

# ---------------------------------------------------------
# 3. TARAMA VE İNDEKSLEME FONKSİYONU
# ---------------------------------------------------------
def harran_tum_siteyi_tara():
    print("🚀 Harran Üniversitesi sitesi derinlemesine taranıyor...")
    
    # Firecrawl Crawl API
    crawl_url = "https://api.firecrawl.dev/v1/crawl"
    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # Tarama konfigürasyonu
    payload = {
        "url": "https://www.harran.edu.tr",
        "limit": 2, # Başlangıç için 100 sayfa (İstersen artırabilirsin)
        "scrapeOptions": {
            "formats": ["markdown"]
        }
    }

    try:
        # Tarama işlemini başlat
        response = requests.post(crawl_url, json=payload, headers=headers, timeout=30)
        response_data = response.json()
        
        # Firecrawl bazen 'id' bazen 'jobId' döner
        job_id = response_data.get("id") or response_data.get("jobId")
        
        if not job_id:
            print(f"❌ Tarama başlatılamadı! API Cevabı: {response_data}")
            return

        print(f"⏳ Tarama başlatıldı. ID: {job_id}. Veriler toplanıyor...")

        # Polling: Tarama bitene kadar bekle
        all_pages = []
        while True:
            status_res = requests.get(f"https://api.firecrawl.dev/v1/crawl/{job_id}", headers=headers)
            status_data = status_res.json()
            
            status = status_data.get("status")
            current_data = status_data.get("data", [])
            
            print(f"📊 Durum: {status} | Şu ana kadar çekilen sayfa: {len(current_data)}")
            
            if status == "completed":
                all_pages = current_data
                break
            elif status == "failed":
                print(f"❌ Tarama başarısız oldu: {status_data.get('error')}")
                return
            
            time.sleep(5) # 5 saniyede bir kontrol et

        # ---------------------------------------------------------
        # 4. VERİLERİ FAISS'E KAYDET
        # ---------------------------------------------------------
        if all_pages:
            print("🔧 Metinler parçalanıyor ve vektör veritabanına ekleniyor...")
            all_chunks = []
            
            for page in all_pages:
                content = page.get("markdown", "")
                if content:
                    chunks = chunk_text(content)
                    all_chunks.extend(chunks)

            if all_chunks:
                add_documents(all_chunks)
                print(f"✨ BAŞARILI! {len(all_chunks)} parça bilgi faiss.index dosyasına kaydedildi.")
            else:
                print("⚠️ Tarama yapıldı ancak işlenecek metin bulunamadı.")
        else:
            print("❌ Hiç sayfa çekilemedi.")

    except Exception as e:
        print(f"❌ Bir hata oluştu: {str(e)}")

if __name__ == "__main__":
    harran_tum_siteyi_tara()