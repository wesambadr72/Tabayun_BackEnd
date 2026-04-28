# app/services/vector_search.py
from sqlalchemy.orm import Session
from sqlalchemy import select, desc
from app.db.models import LegalContent, Category
from app.core.embeddings import generate_embedding

class VectorSearchService:
    """خدمة البحث في pgvector باستخدام استعلامات قاعدة البيانات المباشرة"""

    def __init__(self, db: Session):
        self.db = db

    def search_similar_laws(
        self,
        query_text: str,
        top_k: int = 5,
        country_filter: str | None = None,
        section_filter: str | None = None,
    ) -> list:
        """
        البحث عن قوانين مشابهة باستخدام Vector Similarity مباشرة في PostgreSQL.
        يستخدم هذا التعديل مشغل المسافة (Distance Operator) لـ pgvector لضمان السرعة.
        """

        # 1. توليد embedding للسؤال
        query_embedding = generate_embedding(query_text)

        # 2. بناء الاستعلام الأساسي مع حساب المسافة (Cosine Distance)
        # ملاحظة: cosine_distance = 1 - cosine_similarity
        # لذا الترتيب التصاعدي للمسافة يعطينا الأكثر تشابهاً
        
        distance_query = LegalContent.embedding.cosine_distance(query_embedding).label("distance")
        
        query = self.db.query(LegalContent, distance_query).filter(
            LegalContent.embedding.isnot(None),
            LegalContent.simplified_text != "",
            LegalContent.is_live == 1,
        )

        # 3. تطبيق الفلاتر
        if country_filter:
            query = query.filter(LegalContent.country == country_filter)

        if section_filter:
            category = self.db.query(Category).filter_by(name=section_filter).first()
            if category:
                query = query.filter(LegalContent.category_id == category.id)

        # 4. الترتيب حسب المسافة (الأقرب أولاً) وجلب النتائج
        results = query.order_by("distance").limit(top_k).all()

        # 5. تنسيق النتائج للرد
        formatted_results = []
        for law, distance in results:
            formatted_results.append(
                {
                    "law": law,
                    "similarity": float(1 - distance), # تحويل المسافة إلى تشابه
                    "id": law.id,
                    "title": law.title,
                    "country": law.country,
                    "simplified_text": law.simplified_text,
                    "original_text": law.original_text,
                    "source_url": law.source_url,
                }
            )

        return formatted_results

