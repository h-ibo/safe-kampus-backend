import google.generativeai as genai
import faiss
import pickle
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Gemini Embedding Ayarı
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def get_embedding(text):
    # sentence-transformers yerine Gemini kullanıyoruz (0 MB RAM harcar)
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    return np.array(result['embedding'], dtype='float32')

def search(query, k=5):
    try:
        # Dosyaları yükle
        index = faiss.read_index("faiss.index")
        with open("texts.pkl", "rb") as f:
            texts = pickle.load(f)
        
        # Sorguyu vektöre çevir
        query_vector = get_embedding(query).reshape(1, -1)
        
        # Ara
        distances, indices = index.search(query_vector, k)
        
        results = [texts[i] for i in indices[0] if i != -1]
        return results
    except Exception as e:
        print(f"Arama hatası: {e}")
        return []