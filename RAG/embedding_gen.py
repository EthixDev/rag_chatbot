import google.generativeai as genai
import os

from dotenv import load_dotenv
from RAG.read_chunking import chunk_text,read_pdf

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])


def embed_text(chunk):
    embeddings = genai.embed_content(
        model = 'models/text-embedding-004',
        content=chunk,
    )
    return embeddings["embedding"]  

if __name__ == "__main__":
    doc_path = "/path/to/document"
    
    doc_text = read_pdf(doc_path)
    chunks = chunk_text(doc_text,chunk_size=1500, chunk_overlap=5)
    embeddings = embed_text(chunks)
    print(embeddings)
