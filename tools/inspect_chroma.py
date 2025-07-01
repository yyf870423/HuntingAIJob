import chromadb
import os

CHROMA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "store", "chroma_db")
client = chromadb.PersistentClient(path=CHROMA_PATH)
collection = client.get_or_create_collection("candidates")

result = collection.get(limit=100)
for i, (cid, meta) in enumerate(zip(result['ids'], result['metadatas']), 1):
    print(f"#{i} id: {cid}\nmetadata: {meta}\n{'-'*40}") 