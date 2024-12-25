from langchain.text_splitter import RecursiveCharacterTextSplitter
import fitz  


def read_pdf(file_path):
    pdf_document = fitz.open(file_path)
    text = ""
    
    for page in pdf_document:
        text += page.get_text()  
    
    pdf_document.close() 
    return text


def chunk_text(doc, chunk_size=2000, chunk_overlap=5):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(doc)
    return chunks

if __name__ == "__main__":

    file_path = "/home/meron/Documents/ethix/codes/rag_chatbot/Edge.docx"
    doc_text = read_pdf(file_path)
    doc_text= chunk_text(doc_text)
    print(doc_text)