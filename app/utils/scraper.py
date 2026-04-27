import requests
from bs4 import BeautifulSoup

def harran_scrape(url: str) -> str:
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        text = soup.get_text(separator='\n', strip=True)
        lines = [line for line in text.splitlines() if line.strip()]
        return '\n'.join(lines[:500])
    except Exception as e:
        return f"Sayfa alınamadı: {e}"

def harran_ara(konu: str) -> str:
    url = f"https://www.harran.edu.tr/arama?q={requests.utils.quote(konu)}"
    return harran_scrape(url)
