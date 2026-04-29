import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer

# -------------------------
# MODEL VE YOL AYARLARI
# -------------------------
# MacBook M4 üzerinde bu model çok hızlı çalışır
model = SentenceTransformer("all-MiniLM-L6-v2")
dimension = 384

# Dosya yollarını projenin ana dizinine göre ayarla (Render Uyumlu)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
INDEX_PATH = os.path.join(BASE_DIR, "faiss.index")
TEXT_PATH = os.path.join(BASE_DIR, "texts.pkl")

index = faiss.IndexFlatL2(dimension)
texts = []

# -------------------------
# YÜKLEME VE KAYDETME
# -------------------------
def load_index():
    global index, texts
    if os.path.exists(INDEX_PATH) and os.path.exists(TEXT_PATH):
        try:
            index = faiss.read_index(INDEX_PATH)
            with open(TEXT_PATH, "rb") as f:
                texts = pickle.load(f)
            print("✅ FAISS index ve metinler başarıyla yüklendi.")
        except Exception as e:
            print(f"❌ Index yükleme hatası: {e}")

def save_index():
    faiss.write_index(index, INDEX_PATH)
    with open(TEXT_PATH, "wb") as f:
        pickle.dump(texts, f)
    print(f"💾 Index kaydedildi: {INDEX_PATH}")

# Uygulama başladığında otomatik yükle
load_index()

# -------------------------
# METİN İŞLEME (CHUNK)
# -------------------------
def chunk_text(text: str, max_words: int = 150):
    """Metni anlamlı parçalara böler."""
    if not text: return []
    sentences = text.split(".")
    chunks = []
    current = []
    
    for sentence in sentences:
        words = sentence.split()
        if len(current) + len(words) > max_words:
            chunks.append(" ".join(current))
            current = words
        else:
            current.extend(words)
    if current:
        chunks.append(" ".join(current))
    return [c.strip() for c in chunks if c.strip()]

# -------------------------
# EKLEME VE ARAMA
# -------------------------
def add_documents(docs: list[str]):
    global texts
    if not docs: return

    embeddings = model.encode(docs)
    embeddings = np.array(embeddings).astype("float32")

    index.add(embeddings)
    texts.extend(docs)
    save_index()

def search(query: str, k: int = 3):
    if len(texts) == 0:
        return []

    embedding = model.encode([query])
    embedding = np.array(embedding).astype("float32")

    distances, indices = index.search(embedding, k)

    results = []
    for i in indices[0]:
        if 0 <= i < len(texts):
            results.append(texts[i])
    return results