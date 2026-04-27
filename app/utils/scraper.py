import requests
from bs4 import BeautifulSoup

HEADERS = {'User-Agent': 'Mozilla/5.0'}

HARRAN_SAYFALAR = [
    "https://www.harran.edu.tr",
    "https://www.harran.edu.tr/akademik-takvim",
    "https://www.harran.edu.tr/erasmus",
    "https://www.harran.edu.tr/ogrenci-isleri",
    "https://www.harran.edu.tr/fakulteler",
    "https://www.harran.edu.tr/bolumler",
    "https://www.harran.edu.tr/duyurular",
    "https://www.harran.edu.tr/iletisim",
    "https://www.harran.edu.tr/uluslararasi-iliskiler",
    "https://www.harran.edu.tr/saglik-kulturu-spor",
]

def harran_scrape(url: str) -> str:
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'meta', 'link']):
            tag.decompose()
        text = soup.get_text(separator='\n', strip=True)
        lines = [line for line in text.splitlines() if line.strip() and len(line.strip()) > 3]
        return '\n'.join(lines[:300])
    except Exception as e:
        return f"Sayfa alınamadı: {e}"

def harran_ara(konu: str) -> str:
    # Önce arama sayfasını dene
    url = f"https://www.harran.edu.tr/arama?q={requests.utils.quote(konu)}"
    sonuc = harran_scrape(url)
    
    # Sonra konu ile ilgili tahmin edilen sayfaları dene
    konu_lower = konu.lower()
    ekstra_sayfalar = []
    
    if any(k in konu_lower for k in ['erasmus', 'uluslararası', 'yurtdışı']):
        ekstra_sayfalar.append("https://www.harran.edu.tr/uluslararasi-iliskiler")
    if any(k in konu_lower for k in ['takvim', 'kayıt', 'sınav', 'akademik']):
        ekstra_sayfalar.append("https://www.harran.edu.tr/akademik-takvim")
    if any(k in konu_lower for k in ['bilgisayar', 'mühendis', 'fakülte', 'bölüm']):
        ekstra_sayfalar.append("https://www.harran.edu.tr/muhendislik-fakultesi")
        ekstra_sayfalar.append("https://www.harran.edu.tr/bolum/bilgisayar-muhendisligi")
    if any(k in konu_lower for k in ['öğrenci', 'işleri', 'belge', 'transkript']):
        ekstra_sayfalar.append("https://www.harran.edu.tr/ogrenci-isleri")
    if any(k in konu_lower for k in ['yurt', 'barınma', 'konut']):
        ekstra_sayfalar.append("https://www.harran.edu.tr/saglik-kulturu-spor")
    if any(k in konu_lower for k in ['burs', 'ödeme', 'harç']):
        ekstra_sayfalar.append("https://www.harran.edu.tr/ogrenci-isleri/burs")
    
    for sayfa in ekstra_sayfalar:
        sonuc += "\n\n" + harran_scrape(sayfa)
    
    return sonuc[:3000]

def harran_genel_bilgi() -> str:
    sonuclar = []
    for sayfa in HARRAN_SAYFALAR[:3]:
        sonuclar.append(harran_scrape(sayfa))
    return '\n\n'.join(sonuclar)[:2000]
