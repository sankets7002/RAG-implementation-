import os
from typing import List, Dict
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from groq import Groq
import tiktoken
from PyPDF2 import PdfReader
import numpy as np

# Load environment variables
load_dotenv()

class RAGSystem:
    def __init__(self):
        # Initialize Qdrant client
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Initialize sentence transformer
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Collection name in Qdrant
        self.collection_name = "documents"
        
        # Create collection if it doesn't exist
        self._create_collection()

    def _create_collection(self):
        """Create a collection in Qdrant if it doesn't exist"""
        try:
            self.qdrant_client.get_collection(self.collection_name)
        except:
            self.qdrant_client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=384,  # Dimension of all-MiniLM-L6-v2
                    distance=models.Distance.COSINE
                )
            )

    def process_pdf(self, pdf_path: str, chunk_size: int = 1000) -> List[str]:
        """Process PDF file and split into chunks"""
        pdf_reader = PdfReader(pdf_path)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        # Split text into chunks
        words = text.split()
        chunks = []
        current_chunk = []
        current_size = 0
        
        for word in words:
            current_chunk.append(word)
            current_size += len(word) + 1
            
            if current_size >= chunk_size:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_size = 0
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

    def index_documents(self, documents: List[str]):
        """Index documents in Qdrant"""
        for i, doc in enumerate(documents):
            # Generate embedding
            embedding = self.encoder.encode(doc)
            
            # Upload to Qdrant
            self.qdrant_client.upsert(
                collection_name=self.collection_name,
                points=[
                    models.PointStruct(
                        id=i,
                        vector=embedding.tolist(),
                        payload={"text": doc}
                    )
                ]
            )

    def search(self, query: str, limit: int = 3) -> List[Dict]:
        """Search for relevant documents"""
        query_vector = self.encoder.encode(query)
        
        search_result = self.qdrant_client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=limit
        )
        
        return [{"text": hit.payload["text"], "score": hit.score} for hit in search_result]

    def generate_answer(self, query: str, context: List[Dict]) -> str:
        """Generate answer using Groq"""
        # Prepare context string
        context_str = "\n".join([f"Context {i+1}: {doc['text']}" for i, doc in enumerate(context)])
        
        # Prepare prompt
        prompt = f"""Based on the following context, answer the question. If the answer cannot be found in the context, say "I cannot find the answer in the provided context."

Context:
{context_str}

Question: {query}

Answer:"""

        # Generate response using Groq
        response = self.groq_client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=500
        )
        
        return response.choices[0].message.content

    def query(self, question: str) -> str:
        """Main method to query the RAG system"""
        # Search for relevant documents
        relevant_docs = self.search(question)
        
        # Generate answer
        answer = self.generate_answer(question, relevant_docs)
        
        return answer
        
def main():
    # Initialize the RAG system
    rag_system = RAGSystem()
    
    # Example usage: Index a PDF
    pdf_path = "Air-Writing_Recognition_Based_on_Deep_Convolutiona.pdf"
    if os.path.exists(pdf_path):
        # Process and index PDF
        chunks = rag_system.process_pdf(pdf_path)
        rag_system.index_documents(chunks)
        print(f"Indexed {len(chunks)} document chunks")
    
    # Interactive query loop
    while True:
        question = input("\nEnter your question (or 'quit' to exit): ")
        if question.lower() == 'quit':
            break
            
        answer = rag_system.query(question)
        print(f"\nAnswer: {answer}")

if __name__ == "__main__":
    main()