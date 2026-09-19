import os
try:
    import chromadb
except ImportError:
    chromadb = None

class RunbookStore:
    def __init__(self):
        self.client = chromadb.PersistentClient(path=os.getenv('CHROMA_PATH','./.chroma')) if chromadb else None
        self.collection = self.client.get_or_create_collection('runbooks') if self.client else None
    def add(self, doc_id: str, text: str, metadata: dict | None=None):
        if self.collection: self.collection.upsert(ids=[doc_id], documents=[text], metadatas=[metadata or {}])
    def search(self, query: str, n: int=4):
        if not self.collection: return []
        r=self.collection.query(query_texts=[query], n_results=n)
        return list(zip(r.get('documents',[[]])[0], r.get('metadatas',[[]])[0]))
