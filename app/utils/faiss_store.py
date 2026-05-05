import faiss
import pickle
import os
import numpy as np
import requests
from dotenv import load_dotenv
load_dotenv()

API_KEY = os.getenv("GENAI_API_KEY")

def get_embedding(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={API_KEY}"
    payload = {
        "model": "models/gemini-embedding-001",
        "content": {"parts": [{"text": text}]},
        "taskType": "RETRIEVAL_DOCUMENT"
    }
    response = requests.post(url, json=payload, timeout=30)
    data = response.json()
    if "embedding" not in data:
        raise Exception(f"Embedding hatası: {data}")
    return np.array(data["embedding"]["values"], dtype='float32')

def chunk_text(text, chunk_size=1000):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def add_documents(chunks):
    index_path = "faiss.index"
    pkl_path = "texts.pkl"
    embeddings = []
    for chunk in chunks:
        embeddings.append(get_embedding(chunk))
    embeddings = np.array(embeddings)
    dimension = embeddings.shape[1]
    if os.path.exists(index_path):
        index = faiss.read_index(index_path)
        with open(pkl_path, "rb") as f:
            texts = pickle.load(f)
    else:
        index = faiss.IndexFlatL2(dimension)
        texts = []
    index.add(embeddings)
    texts.extend(chunks)
    faiss.write_index(index, index_path)
    with open(pkl_path, "wb") as f:
        pickle.dump(texts, f)

def search(query, k=5):
    try:
        if not os.path.exists("faiss.index"): return []
        index = faiss.read_index("faiss.index")
        with open("texts.pkl", "rb") as f:
            texts = pickle.load(f)
        query_vector = get_embedding(query).reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        return [texts[i] for i in indices[0] if i != -1]
    except Exception as e:
        print(f"Arama hatası: {e}")
        return []

if __name__ == "__main__":
    print("🚀 Model testi başlatılıyor...")
    try:
        test_res = get_embedding("Harran Üniversitesi")
        print(f"✅ BAŞARILI! Vektör boyutu: {len(test_res)}")
    except Exception as e:
        print(f"❌ HATA: {e}")
