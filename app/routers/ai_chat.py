from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from app.utils.faiss_store import search 

load_dotenv()

router = APIRouter()

# Gemini Ayarları
GENAI_API_KEY = os.getenv("GENAI_API_KEY")
if not GENAI_API_KEY:
    raise ValueError("GENAI_API_KEY bulunamadı!")

genai.configure(api_key=GENAI_API_KEY)

# --- MODEL LİSTELEME VE SEÇME ---
try:
    print("🚀 Render üzerinde kullanılabilir modeller taranıyor...")
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    for model_name in available_models:
        print(f"✅ Kullanılabilir Model: {model_name}")
    
    # Eğer gemini-1.5-flash listede varsa onu seç, yoksa listedeki ilk modeli al
    selected_model_name = 'models/gemini-1.5-flash' if 'models/gemini-1.5-flash' in available_models else available_models[0]
    print(f"🎯 Seçilen Model: {selected_model_name}")
    model = genai.GenerativeModel(selected_model_name)
except Exception as e:
    print(f"❌ Model listeleme hatası: {e}")
    # Yedek plan
    model = genai.GenerativeModel('gemini-1.5-flash')

class ChatRequest(BaseModel):
    soru: str

@router.post("/ai-chat/")
async def chat(request: ChatRequest):
    try:
        context_docs = search(request.soru, k=5)
        context_text = "\n\n".join(context_docs)

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

        response = model.generate_content(prompt)
        
        return {
            "cevap": response.text,
            "kaynaklar": len(context_docs)
        }

    except Exception as e:
        print(f"Chat Hatası: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Bir hata oluştu: {str(e)}")