from sqlalchemy.orm import Session
from app.db.vector_search import VectorSearchService
from app.services.gemini_service import geminiService


class RAGPipeline:
    """Pipeline كامل لـ RAG"""

    def __init__(self, db: Session):
        self.db = db
        self.vector_search = VectorSearchService(db)
        self.gemini = geminiService()

    def answer_question(
        self,
        question: str,
        country_filter: str | None = None,
        section_filter: str | None = None,
    ) -> dict:
        """الإجابة على سؤال باستخدام RAG"""

        similar_laws = self.vector_search.search_similar_laws(
            question,
            top_k=5,
            country_filter=country_filter,
            section_filter=section_filter,
        )

        if not similar_laws:
            return {
                "answer": "عذراً، لم أجد معلومات قانونية ذات صلة بسؤالك.",
                "sources": [],
                "context_used": 0,
            }

        context = self._build_context(similar_laws)
        answer = self.gemini.generate_with_context(question, context)
        sources = self._extract_sources(similar_laws)

        return {
            "answer": answer or "عذراً، حدث خطأ في معالجة السؤال.",
            "sources": sources,
            "context_used": len(similar_laws),
        }

    def _build_context(self, results: list) -> str:
        parts = []
        for idx, result in enumerate(results, 1):
            parts.append(
                f"### مصدر {idx}: {result['country']} - {result['title']}\n"
                f"{result['simplified_text']}"
            )
        return "\n\n".join(parts)

    def _extract_sources(self, results: list) -> list:
        return [
            {
                "id": r["id"],
                "country": r["country"],
                "title": r["title"],
                "url": r["source_url"],
                "similarity": round(r["similarity"] * 100, 1),
            }
            for r in results[:3]
        ]
