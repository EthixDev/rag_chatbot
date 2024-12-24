from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv
from .read_chunking import read_docx, chunk_text

load_dotenv()

def embed_text(chunks):
    embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
    embeds = embedding_model.embed_documents(chunks)
    return embeds

if __name__ == "__main__":
    doc_path = "/path/to/document.docx"
    
    doc_text = read_docx(doc_path)
    chunks = chunk_text(doc_text,chunk_size=1500, chunk_overlap=5)
    embeddings = embed_text(chunks)
    print(embeddings)
