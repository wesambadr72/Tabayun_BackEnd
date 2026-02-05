from sentence_transformers import SentenceTransformer
from functools import lru_cache

@lru_cache(maxsize=1)
# تحميل النموذج مرة واحدة فقط
def get_embedding_model():
    return SentenceTransformer(settings.EMBEDDING_MODEL)

def generate_embedding(text: str) -> list:
    # توليد embedding للنص المحدد
    model = get_embedding_model()
    return model.encode(text).tolist()

def generate_embeddings(texts: list[str]) -> list:
    # توليد embeddings لعدة نصوص
    model = get_embedding_model()
    return model.encode(texts).tolist()