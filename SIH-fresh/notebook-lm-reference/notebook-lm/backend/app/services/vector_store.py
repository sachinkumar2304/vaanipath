import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional
from sentence_transformers import SentenceTransformer


class VectorStore:
    """Local vector store using FAISS"""

    def __init__(self, embedding_model: str, vector_db_dir: Path):
        self.embedding_model = SentenceTransformer(embedding_model)
        self.vector_db_dir = vector_db_dir
        self.dimension = self.embedding_model.get_sentence_embedding_dimension()
        self.documents = {}  # document_id -> {index, chunks, metadata}

    def _get_index_path(self, document_id: str) -> Path:
        """Get path to FAISS index file for a document"""
        return self.vector_db_dir / f"{document_id}.faiss"

    def _get_metadata_path(self, document_id: str) -> Path:
        """Get path to metadata file for a document"""
        return self.vector_db_dir / f"{document_id}_metadata.pkl"

    def create_embeddings(self, texts: List[str]) -> np.ndarray:
        """Create embeddings for a list of texts"""
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        return np.array(embeddings).astype('float32')

    def add_document(self, document_id: str, chunks: List[Tuple[str, dict]]) -> int:
        """
        Add a document to the vector store.
        Returns the number of chunks added.
        """
        # Extract texts and metadata
        texts = [chunk[0] for chunk in chunks]
        metadata = [chunk[1] for chunk in chunks]

        # Create embeddings
        embeddings = self.create_embeddings(texts)

        # Create FAISS index
        index = faiss.IndexFlatL2(self.dimension)
        index.add(embeddings)

        # Save index and metadata
        faiss.write_index(index, str(self._get_index_path(document_id)))

        with open(self._get_metadata_path(document_id), 'wb') as f:
            pickle.dump({'chunks': texts, 'metadata': metadata}, f)

        # Store in memory
        self.documents[document_id] = {
            'index': index,
            'chunks': texts,
            'metadata': metadata
        }

        return len(chunks)

    def load_document(self, document_id: str) -> bool:
        """Load a document from disk into memory"""
        index_path = self._get_index_path(document_id)
        metadata_path = self._get_metadata_path(document_id)

        if not index_path.exists() or not metadata_path.exists():
            return False

        # Load index
        index = faiss.read_index(str(index_path))

        # Load metadata
        with open(metadata_path, 'rb') as f:
            data = pickle.load(f)

        self.documents[document_id] = {
            'index': index,
            'chunks': data['chunks'],
            'metadata': data['metadata']
        }

        return True

    def search(
        self,
        document_id: str,
        query: str,
        top_k: int = 3
    ) -> List[Tuple[str, dict, float]]:
        """
        Search for relevant chunks in a document.
        Returns list of (chunk_text, metadata, distance) tuples.
        """
        # Load document if not in memory
        if document_id not in self.documents:
            if not self.load_document(document_id):
                return []

        doc_data = self.documents[document_id]

        # Create query embedding
        query_embedding = self.create_embeddings([query])

        # Search in FAISS index
        distances, indices = doc_data['index'].search(query_embedding, top_k)

        # Prepare results
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(doc_data['chunks']):
                results.append((
                    doc_data['chunks'][idx],
                    doc_data['metadata'][idx],
                    float(distance)
                ))

        return results

    def document_exists(self, document_id: str) -> bool:
        """Check if a document exists in the vector store"""
        return (
            self._get_index_path(document_id).exists() and
            self._get_metadata_path(document_id).exists()
        )

    def get_all_chunks(self, document_id: str) -> Optional[List[str]]:
        """Get all chunks for a document"""
        if document_id not in self.documents:
            if not self.load_document(document_id):
                return None

        return self.documents[document_id]['chunks']
