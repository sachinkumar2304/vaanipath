import pymupdf
from pathlib import Path
from typing import List, Tuple
import hashlib


class PDFProcessor:
    """Process PDF documents for RAG system"""

    def __init__(self, chunk_size: int = 512, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def extract_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        doc = pymupdf.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def chunk_text(self, text: str) -> List[Tuple[str, dict]]:
        """
        Chunk text using fixed-size chunking with overlap.
        Returns list of (chunk_text, metadata) tuples.
        """
        words = text.split()
        chunks = []

        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = " ".join(chunk_words)

            metadata = {
                "chunk_id": i // (self.chunk_size - self.chunk_overlap),
                "start_word": i,
                "end_word": i + len(chunk_words),
            }

            chunks.append((chunk_text, metadata))

            if i + self.chunk_size >= len(words):
                break

        return chunks

    def process_pdf(self, pdf_path: Path) -> Tuple[str, List[Tuple[str, dict]]]:
        """
        Process PDF: extract text and chunk it.
        Returns (document_id, chunks).
        """
        # Generate document ID from file hash
        with open(pdf_path, "rb") as f:
            file_hash = hashlib.sha256(f.read()).hexdigest()[:16]

        # Extract and chunk text
        text = self.extract_text(pdf_path)
        chunks = self.chunk_text(text)

        return file_hash, chunks
