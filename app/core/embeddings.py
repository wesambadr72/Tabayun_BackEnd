from sentence_transformers import SentenceTransformer
from functools import lru_cache
from app.core.config import settings

@lru_cache(maxsize=1)
def get_embedding_model():
    # تنظيف اسم الموديل من أي علامات تنصيص
    model_name = settings.EMBEDDING_MODEL.strip('"').strip("'")
    if not model_name:
        model_name = "paraphrase-multilingual-MiniLM-L12-v2"
    
    print(f"📡 Loading Multilingual Model: {model_name}...")
    return SentenceTransformer(model_name)

def generate_embedding(text: str) -> list:
    # توليد embedding للنص المحدد
    model = get_embedding_model()
    return model.encode(text).tolist()

def generate_embeddings(texts: list[str]) -> list:
    # توليد embeddings لعدة نصوص
    model = get_embedding_model()
    return model.encode(texts).tolist()