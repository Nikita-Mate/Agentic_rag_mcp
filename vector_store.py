# vector_store.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import pickle

class VectorStore:
    def __init__(self, persist_path="vector_store"):
        self.persist_path = persist_path
        self.index_path = os.path.join(persist_path, "faiss_index")
        self.chunks_path = os.path.join(persist_path, "chunks.pkl")
        
        try:
            self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self.text_chunks = []
            self.index = None
            self._load_or_create_index()
        except Exception as e:
            print(f"VectorStore initialization error: {str(e)}")
            raise
    
    def _load_or_create_index(self):
        try:
            if os.path.exists(self.index_path) and os.path.exists(self.chunks_path):
                self.index = faiss.read_index(self.index_path)
                with open(self.chunks_path, 'rb') as f:
                    self.text_chunks = pickle.load(f)
                print(f"Loaded existing index with {len(self.text_chunks)} documents")
            else:
                self.index = faiss.IndexFlatL2(384)
                self.text_chunks = []
                os.makedirs(self.persist_path, exist_ok=True)
                print("Created new vector store")
        except Exception as e:
            print(f"Error loading/creating index: {str(e)}")
            self.index = faiss.IndexFlatL2(384)
            self.text_chunks = []
    
    def add_documents(self, chunks):
        try:
            valid_chunks = [chunk for chunk in chunks if chunk and chunk.strip()]
            if not valid_chunks:
                return
            
            embeddings = self.model.encode(valid_chunks)
            embeddings = np.array(embeddings).astype("float32")
            if embeddings.ndim == 1:
                embeddings = embeddings.reshape(1, -1)
            
            self.index.add(embeddings)
            self.text_chunks.extend(valid_chunks)
            self._save_index()
        except Exception as e:
            print(f"Error adding documents: {str(e)}")
            raise
    
    def _save_index(self):
        try:
            faiss.write_index(self.index, self.index_path)
            with open(self.chunks_path, 'wb') as f:
                pickle.dump(self.text_chunks, f)
        except Exception as e:
            print(f"Error saving index: {str(e)}")
    
    def retrieve(self, query, top_k=3):
        try:
            if self.index.ntotal == 0:
                return []
            
            actual_top_k = min(top_k, self.index.ntotal)
            query_emb = self.model.encode([query])
            query_emb = np.array(query_emb).astype("float32")
            
            distances, indices = self.index.search(query_emb, actual_top_k)
            
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.text_chunks):  
                    results.append({
                        'text': self.text_chunks[idx],
                        'distance': distances[0][i],
                        'index': idx
                    })
            return results            
        except Exception as e:
            print(f"Error retrieving documents: {str(e)}")
            return []
    
    def clear(self):
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
            if os.path.exists(self.chunks_path):
                os.remove(self.chunks_path)
            if os.path.exists(self.persist_path):
                os.rmdir(self.persist_path)
            print("Vector store cleared")
        except Exception as e:
            print(f"Error clearing vector store: {str(e)}")
    
    def get_stats(self):
        return {
            'total_documents': len(self.text_chunks),
            'index_size': self.index.ntotal,
            'embedding_dimension': self.index.d
        }
