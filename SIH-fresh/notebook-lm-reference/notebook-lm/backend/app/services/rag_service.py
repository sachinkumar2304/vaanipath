from typing import List, Tuple
from langchain_groq import ChatGroq
import httpx
import json


class RAGService:
    """RAG service for answering questions based on document context"""

    def __init__(
        self,
        vector_store,
        groq_api_key: str = None,
        ollama_base_url: str = "http://localhost:11434",
        ollama_model: str = "llama3.2:latest"
    ):
        self.vector_store = vector_store
        self.groq_api_key = groq_api_key
        self.ollama_base_url = ollama_base_url
        self.ollama_model = ollama_model

        # Initialize LLM (prefer Groq API if available)
        self.use_ollama = True
        self.llm = None
        if groq_api_key:
            try:
                # Use llama-3.3-70b-versatile (active model as of 2024)
                # See: https://console.groq.com/docs/models
                self.llm = ChatGroq(
                    groq_api_key=groq_api_key,
                    model_name="llama-3.3-70b-versatile"
                )
                self.use_ollama = False
                print(f"✅ RAG Service: Using Groq API (llama-3.3-70b-versatile)")
            except Exception as e:
                print(f"⚠️  RAG Service: Groq init failed ({e}), will use Ollama")
        else:
            print(f"ℹ️  RAG Service: No Groq API key, using local Ollama")

    def _query_ollama(self, prompt: str) -> str:
        """Query local Ollama model"""
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.ollama_model,
                        "prompt": prompt,
                        "stream": False
                    }
                )
                if response.status_code == 200:
                    return response.json()["response"]
                else:
                    return "Error: Unable to get response from Ollama"
        except Exception as e:
            return f"Error connecting to Ollama: {str(e)}"

    def generate_answer(
        self,
        document_id: str,
        question: str,
        top_k: int = 3
    ) -> Tuple[str, List[str]]:
        """
        Generate an answer to a question using RAG.
        Returns (answer, source_chunks).
        """
        # Retrieve relevant chunks
        results = self.vector_store.search(document_id, question, top_k)

        if not results:
            return "No relevant information found in the document.", []

        # Prepare context from retrieved chunks
        context = "\n\n".join([chunk for chunk, _, _ in results])
        source_chunks = [chunk for chunk, _, _ in results]

        # Create prompt
        prompt = f"""You are a helpful assistant that answers questions based on the provided context.

Context:
{context}

Question: {question}

Please provide a clear and concise answer based only on the context provided. If the answer cannot be found in the context, say so.

Answer:"""

        # Generate answer - Groq is prioritized
        if self.use_ollama:
            print("🤖 RAG: Using Ollama for answer generation...")
            answer = self._query_ollama(prompt)
        else:
            print("🤖 RAG: Using Groq API for answer generation...")
            response = self.llm.invoke(prompt)
            answer = response.content
            print("✅ RAG: Successfully generated answer from Groq")

        return answer, source_chunks
