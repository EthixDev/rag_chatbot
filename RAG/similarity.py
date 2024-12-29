from pgvector.django import CosineDistance
def cosine_similarity(embedding1, embedding2):
    
    return CosineDistance(embedding1, embedding2)