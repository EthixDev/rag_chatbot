from RAG.embedding_gen import embed_text

sample_text = "Sample input for testing the embedding dimension."
embedding = embed_text(sample_text)
print(f"Embedding Dimension: {len(embedding)}")
