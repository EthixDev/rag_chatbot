# from langchain_community.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
from RAG.read_chunking import chunk_text,read_docx
from sentence_transformers import SentenceTransformer
# 

load_dotenv()

# def embed_text(chunks):
#     embedding_model = OpenAIEmbeddings(model="text-embedding-ada-002")
#     embeds = embedding_model.embed_documents(chunks)
#     return embeds


def embed_text(chunks):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = model.encode(chunks, convert_to_tensor=True)
    return embeddings

if __name__ == "__main__":
    doc_path = "/home/meron/Documents/ethix/codes/rag_chatbot/Edge.docx"
    
    doc_text = read_docx(doc_path)
    chunks = chunk_text(doc_text,chunk_size=1500, chunk_overlap=5)
    embeddings = embed_text(chunks)
    print(embeddings)
