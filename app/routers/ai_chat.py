from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.utils.faiss_store import search # Senin yazdığın arama fonksiyonu

load_dotenv()

router = APIRouter()

# Gemini Ayarları
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY bulunamadı!")

genai.configure(api_key=GENAI_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

class ChatRequest(BaseModel):
    soru: str

@router.post("/ai-chat/")
async def chat(request: ChatRequest):
    try:
        # 1. ADIM: FAISS hafızasından alakalı bilgileri getir
        # k=5 yaparak en alakalı 5 parçayı alıyoruz
        context_docs = search(request.soru, k=5)
        context_text = "\n\n".join(context_docs)

        # 2. ADIM: Gemini için sistem komutunu (Prompt) oluştur
        # Eğer hafızada bilgi yoksa genel bilgisini kullanmasını söylüyoruz
        prompt = f"""
        Sen Harran Üniversitesi için geliştirilmiş 'SafeKampüs' asistanısın. 
        Görevin, aşağıda sana sağlanan bilgiler (BAĞLAM) doğrultusunda öğrencinin sorusunu cevaplamaktır.
        
        KURALLAR:
        1. Sadece sağlanan bağlama sadık kalarak cevap ver.
        2. Eğer bağlamda cevap yoksa, "Bu konuda üniversite veritabanında net bir bilgi bulamadım, ancak genel olarak..." diyerek devam edebilirsin.
        3. Nazik, yardımsever ve bir üniversite asistanı gibi profesyonel konuş.
        
        BAĞLAM (Harran Üniversitesi Verileri):
        {context_text if context_text else "Üniversite veritabanında bu soruyla ilgili spesifik bir döküman bulunamadı."}
        
        KULLANICI SORUSU:
        {request.soru}
        """

        # 3. ADIM: Gemini'den cevabı al
        response = model.generate_content(prompt)
        
        return {
            "cevap": response.text,
            "kaynaklar": len(context_docs) # Kaç parça bilgiden faydalandığını görmek için
        }

    except Exception as e:
        print(f"Chat Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")