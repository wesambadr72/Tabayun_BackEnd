from sqlalchemy.orm import Session
from app.services.vector_search import VectorSearchService
from app.services.gemini_service import GeminiService


class RAGPipeline:
    """Pipeline كامل لـ RAG"""

    def __init__(self, db: Session):
        self.db = db
        self.vector_search = VectorSearchService(db)
        self.gemini = GeminiService()

    async def answer_question(
        self,
        question: str,
        country_filter: str | None = None,
        section_filter: str | None = None,
        language: str = "ar",
    ) -> dict:
        """الإجابة على سؤال باستخدام RAG"""

        similar_laws = self.vector_search.search_similar_laws(
            question,
            top_k=7,
            country_filter=country_filter,
            section_filter=section_filter,
        )

        if not similar_laws:
            return {
                "answer": "عذراً، لم أجد معلومات قانونية ذات صلة بسؤالك." if language == "ar" else "Sorry, I couldn't find any relevant legal information.",
                "sources": [],
                "context_used": 0,
            }
        
        context = self._build_context(similar_laws)
        answer = await self.gemini.generate_with_context(question, context, language=language)
        sources = self._extract_sources(similar_laws)

        return {
            "answer": answer or ("عذراً، حدث خطأ في معالجة السؤال." if language == "ar" else "Sorry, an error occurred while processing your question."),
            "sources": sources,
            "context_used": len(similar_laws),
        }

    def _build_context(self, results: list) -> str:
        parts = []
        for idx, result in enumerate(results, 1):
            parts.append(
                f"### مصدر {idx}: {result['country']} - {result['title']}\n"
                f"{result['original_text']}"
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
