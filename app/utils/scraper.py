import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.harran.edu.tr"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "tr-TR,tr;q=0.9"
}

# -----------------------
# SAYFA ÇEKME
# -----------------------
def harran_scrape(url: str) -> str:
    try:
        res = requests.get(url, headers=HEADERS, timeout=10)
        res.raise_for_status()

        soup = BeautifulSoup(res.text, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        main = soup.find("main") or soup.body

        text = main.get_text(separator="\n", strip=True)

        lines = [
            line.strip()
            for line in text.splitlines()
            if len(line.strip()) > 25
        ]

        return "\n".join(lines[:200])

    except Exception as e:
        return f"Hata: {e}"


# -----------------------
# LİNK TOPLAMA
# -----------------------
def linkleri_topla():
    try:
        res = requests.get(BASE_URL, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

            if href.startswith("/"):
                links.add(urljoin(BASE_URL, href))

        return list(links)

    except:
        return []


# -----------------------
# AKILLI SKORLAMA (EN ÖNEMLİ FIX)
# -----------------------
def link_filtrele(links, konu):
    konu = konu.lower().split()

    scored = []

    for link in links:
        link_l = link.lower()

        score = 0
        for k in konu:
            if k in link_l:
                score += 1

        if score > 0:
            scored.append((score, link))

    scored.sort(reverse=True, key=lambda x: x[0])

    return [l for _, l in scored[:5]]


# -----------------------
# ANA ARAMA
# -----------------------
def harran_ara(konu: str) -> str:
    links = linkleri_topla()

    uygun_linkler = link_filtrele(links, konu)

    if not uygun_linkler:
        return "Uygun sayfa bulunamadı."

    sonuc = ""

    for link in uygun_linkler:
        sonuc += f"\n--- {link} ---\n"
        sonuc += harran_scrape(link) + "\n"

    return sonuc[:3000]