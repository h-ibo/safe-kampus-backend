import os
import requests
from dotenv import load_dotenv

load_dotenv()

FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

if not FIRECRAWL_API_KEY:
    # Render'da Environment Variables kısmına eklemeyi unutma!
    print("UYARI: FIRECRAWL_API_KEY bulunamadı!")

BASE_URL = "https://api.firecrawl.dev/v1/scrape"

def firecrawl_get(url: str):
    """
    Web sayfasını scrape eder ve temiz Markdown metni döner.
    """
    if not FIRECRAWL_API_KEY:
        return ""

    headers = {
        "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "url": url,
        "formats": ["markdown"]
    }

    try:
        # Üniversite siteleri bazen ağır yüklenebilir, timeout'u 60 yaptık
        response = requests.post(
            BASE_URL,
            json=payload,
            headers=headers,
            timeout=60 
        )

        if response.status_code != 200:
            print(f"Firecrawl Hatası ({url}): {response.text}")
            return ""

        data = response.json()
        return data.get("data", {}).get("markdown", "")

    except Exception as e:
        print(f"Firecrawl İsteği Başarısız: {str(e)}")
        return ""