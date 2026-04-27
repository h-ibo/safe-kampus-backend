import os
import google.generativeai as genai
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.utils.dependencies import get_current_user
from app.utils.scraper import harran_scrape, harran_ara

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

class SoruRequest(BaseModel):
    soru: str

@router.post("/")
async def ai_sohbet(
    request: SoruRequest,
    current_user=Depends(get_current_user)
):
    try:
        # Harran sitesinden bilgi çek
        ana_sayfa = harran_scrape("https://www.harran.edu.tr")
        arama = harran_ara(request.soru)
        
        prompt = f"""Sen Harran Üniversitesi asistanısın. Sadece Harran Üniversitesi hakkında sorulara cevap ver.
        
Harran Üniversitesi web sitesinden alınan bilgiler:
{ana_sayfa[:1000]}

Arama sonuçları ({request.soru}):
{arama[:1000]}

Öğrencinin sorusu: {request.soru}

Türkçe, kısa ve net cevap ver. Eğer bilgi bulamazsan 'Bu konuda bilgim bulunmuyor, harran.edu.tr adresini ziyaret edebilirsiniz' de."""

        response = model.generate_content(prompt)
        return {"cevap": response.text}
    except Exception as e:
        return {"cevap": f"Bir hata oluştu: {str(e)}"}
