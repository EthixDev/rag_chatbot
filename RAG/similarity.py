import numpy as np
from numpy.linalg import norm

def cosine_similarity(embedding1, embedding2):
    
    return np.dot(embedding1, embedding2) / (norm(embedding1) * norm(embedding2))