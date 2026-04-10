# app/db/vector_search.py
from sqlalchemy.orm import Session
from app.db.models import LegalContent, Category
from app.core.embeddings import generate_embedding
import numpy as np


class VectorSearchService:
    """خدمة البحث في pgvector"""

    def __init__(self, db: Session):
        self.db = db

    def search_similar_laws(
        self,
        query_text: str,
        top_k: int = 5,
        country_filter: str | None = None,
        section_filter: str | None = None,
    ) -> list:
        """البحث عن قوانين مشابهة باستخدام Vector Similarity"""

        # 1. توليد embedding للسؤال
        query_embedding = generate_embedding(query_text)

        # 2. بناء الـ query
        query = self.db.query(LegalContent).filter(
            LegalContent.embedding.isnot(None),
            LegalContent.simplified_text != "",
            LegalContent.is_live == 1,
        )

        # 3. الفلاتر
        if country_filter:
            query = query.filter(LegalContent.country == country_filter)

        if section_filter:
            category = self.db.query(Category).filter_by(name=section_filter).first()
            if category:
                query = query.filter(LegalContent.category_id == category.id)

        # 4. جلب النتائج
        all_laws = query.all()

        # 5. حساب التشابه (Cosine Similarity)
        similarities = []
        for law in all_laws:
            if law.embedding is not None:
                law_embedding = np.array(law.embedding)
                query_emb = np.array(query_embedding)

                similarity = np.dot(query_emb, law_embedding) / (
                    np.linalg.norm(query_emb) * np.linalg.norm(law_embedding)
                )

                similarities.append(
                    {
                        "law": law,
                        "similarity": float(similarity),
                        "id": law.id,
                        "title": law.title,
                        "country": law.country,
                        "simplified_text": law.simplified_text,
                        "source_url": law.source_url,
                    }
                )

        # 6. ترتيب حسب التشابه
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        return similarities[:top_k]

