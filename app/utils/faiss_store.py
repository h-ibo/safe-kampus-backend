import google.generativeai as genai
import faiss
import pickle
import os
import numpy as np
from dotenv import load_dotenv

load_dotenv()

# Gemini Embedding Ayarı (Ücretsiz ve RAM harcamaz)
genai.configure(api_key=os.getenv("GENAI_API_KEY"))

def get_embedding(text):
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=text,
        task_type="retrieval_query"
    )
    return np.array(result['embedding'], dtype='float32')

def search(query, k=5):
    try:
        # Render'daki dosya yoluna göre yükle
        index_path = "faiss.index"
        pkl_path = "texts.pkl"
        
        if not os.path.exists(index_path):
            return []

        index = faiss.read_index(index_path)
        with open(pkl_path, "rb") as f:
            texts = pickle.load(f)
        
        query_vector = get_embedding(query).reshape(1, -1)
        distances, indices = index.search(query_vector, k)
        
        results = [texts[i] for i in indices[0] if i != -1]
        return results
    except Exception as e:
        print(f"Arama hatası: {e}")
        return []