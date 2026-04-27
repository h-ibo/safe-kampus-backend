import os
import requests as req
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.utils.dependencies import get_current_user
from app.utils.scraper import harran_scrape, harran_ara

router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])

class SoruRequest(BaseModel):
    soru: str

@router.post("/")
async def ai_sohbet(
    request: SoruRequest,
    current_user=Depends(get_current_user)
):
    try:
        ana_sayfa = harran_scrape("https://www.harran.edu.tr")
        arama = harran_ara(request.soru)
        
        prompt = f"""Sen Harran Üniversitesi asistanısın. Sadece Harran Üniversitesi hakkında sorulara cevap ver.

Harran Üniversitesi web sitesinden alınan bilgiler:
{ana_sayfa[:1000]}

Arama sonuçları ({request.soru}):
{arama[:1000]}

Öğrencinin sorusu: {request.soru}

Türkçe, kısa ve net cevap ver."""

        api_key = os.getenv("GEMINI_API_KEY")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        response = req.post(url, json=payload, timeout=30)
        data = response.json()
        
        if "candidates" not in data:
            return {"cevap": f"API Hatası: {data}"}
        
        cevap = data["candidates"][0]["content"]["parts"][0]["text"]
        return {"cevap": cevap}
    except Exception as e:
        return {"cevap": f"Bir hata oluştu: {str(e)}"}
