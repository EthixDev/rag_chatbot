from django.db import models
from pgvector.django import VectorField
from RAG.read_chunking import read_docx, chunk_text
from RAG.embedding_gen import embed_text
import logging

logger = logging.getLogger(__name__)

class Document(models.Model):
    file = models.FileField(upload_to='documents/')
    title = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title or f"Document uploaded on {self.created_at}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        if self.file:
            try:
                text = read_docx(self.file.path)
                chunks = chunk_text(text)
                
                # Generate embeddings for the chunks
                for chunk in chunks:
                    embed = embed_text(chunk)
                    if not isinstance(embed, list) or not all(isinstance(val, float) for val in embed):
                        raise ValueError("Embedding is not a valid list of floats")
                    
                    # Save the chunk and its embedding
                    TextChunk.objects.create(document=self, chunk=chunk, embedding=embed)
            except Exception as e:
                logger.error(f"Error processing document: {e}")
                raise

class TextChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='text_chunks')       
    chunk = models.TextField()
    embedding = VectorField() 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Chunk for Document ID {self.document.id}"  
    
class Topic(models.Model):
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Conversation(models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null = True)
    question = models.CharField(max_length=500)
    answer = models.CharField(max_length=2000)
    created_at = models.DateTimeField(auto_now_add=True)
    

                
            
