import numpy as np
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType


def cosine_similarity(vector_a, vector_b):
    vector_a = np.array(vector_a)
    vector_b = np.array(vector_b)
    dot_product = np.dot(vector_a, vector_b)
    norm_a = np.linalg.norm(vector_a)
    norm_b = np.linalg.norm(vector_b)
    return dot_product / (norm_a * norm_b)


def _emb(text: str):
    embed_model = OpenAIEmbedding(model="text-embedding-3-large")
    embeddings = embed_model.get_text_embedding(text)
    return embeddings


similarity = cosine_similarity(_emb("Talinn"), _emb("Estonia"))
print(f"Cosine Similarity: {similarity:.3f}")

similarity = cosine_similarity(_emb("Python"), _emb("Java"))
print(f"Cosine Similarity: {similarity:.3f}")

similarity = cosine_similarity(_emb("Python"), _emb("Estonia"))
print(f"Cosine Similarity: {similarity:.3f}")
