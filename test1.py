from app.utils.firecrawl import firecrawl_get
from app.rag.faiss_store import chunk_text, add_documents, search, load_index

url = "https://www.harran.edu.tr"

print("SCRAPING...")
text = firecrawl_get(url)

print("CHUNKING...")
chunks = chunk_text(text)

print("INDEXING...")
add_documents(chunks)

print("SEARCH:")
print(search("bilgisayar mühendisliği nedir"))