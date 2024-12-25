from langchain.text_splitter import RecursiveCharacterTextSplitter
from docx import Document

def read_docx(file_path):
    doc = Document(file_path)
    text = ""
    
    for para in doc.paragraphs:
        text += para.text
    
    return text

def chunk_text(doc, chunk_size=2000, chunk_overlap=5):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(doc)
    return chunks

if __name__ == "__main__":
    file_path = "/path/to/document.docx"
    doc_text = read_docx(file_path)
    print(doc_text)