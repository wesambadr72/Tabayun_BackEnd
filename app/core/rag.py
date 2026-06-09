from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import ComparativeLaw
from app.services.openai_service import OpenAIService
from app.services.source_fetcher import SourceFetcher
from app.services.vector_search import VectorSearchService

MIN_CHAT_SIMILARITY = 0.4

COUNTRY_ALIASES = {
    "sa": {"sa", "ksa", "saudi", "saudi arabia", "السعودية", "المملكة العربية السعودية"},
    "uk": {"uk", "united kingdom", "britain", "great britain", "بريطانيا", "المملكة المتحدة"},
    "de": {"de", "germany", "german", "ألمانيا", "المانيا"},
    "us": {"us", "usa", "united states", "america", "أمريكا", "الولايات المتحدة"},
}


class RAGPipeline:
    """RAG pipeline for answering legal questions."""

    def __init__(self, db: Session):
        self.db = db
        self.vector_search = VectorSearchService(db)
        self.openai = OpenAIService()
        self.source_fetcher = SourceFetcher()

    async def answer_question(
        self,
        question: str,
        country_filter: str | None = None,
        section_filter: str | None = None,
        language: str = "ar",
        user_name: str | None = None,
        user_country: str | None = None,
    ) -> dict:
        similar_laws = self.vector_search.search_similar_laws(
            question,
            top_k=10,
            country_filter=country_filter,
            section_filter=section_filter,
        )
        similar_laws = [
            law for law in similar_laws
            if law.get("similarity", 0) >= MIN_CHAT_SIMILARITY
        ]

        if not similar_laws:
            display_name = self._display_name(user_name, language)
            return {
                "answer": (
                    f"ما لقيت مرجعًا واضحًا يجاوب على سؤالك يا {display_name}. اكتب لي البلد أو تفاصيل الحالة أكثر، وأبحث لك من جديد."
                    if language == "ar"
                    else f"I could not find a clear source that answers this, {display_name}. Add the country or a few more details and I will search again."
                ),
                "sources": [],
                "context_used": 0,
            }

        context = await self._build_context(similar_laws, user_country=user_country)
        answer = await self.openai.generate_with_context(
            question,
            context,
            language=language,
            user_name=user_name,
            user_country=user_country,
        )
        sources = self._extract_sources(similar_laws)

        return {
            "answer": answer or (
                "عذرًا، حدث خطأ في معالجة السؤال."
                if language == "ar"
                else "Sorry, an error occurred while processing your question."
            ),
            "sources": sources,
            "context_used": len(similar_laws),
        }

    async def _build_context(self, results: list, user_country: str | None = None) -> str:
        parts = []
        for idx, result in enumerate(results, 1):
            parts.append(await self._format_law_context(idx, result))

        comparison_context = await self._build_comparison_context(results, user_country)
        if comparison_context:
            parts.append(comparison_context)

        return "\n\n".join(parts)

    async def _format_law_context(self, idx: int, result: dict) -> str:
        fetched_text = await self.source_fetcher.fetch_text(result.get("source_url"))
        live_reference = (
            f"\n\nText fetched from the same source URL:\n{fetched_text}"
            if fetched_text
            else ""
        )
        return (
            f"### Source {idx}: {result['country']} - {result['title']}\n"
            f"Source URL: {result.get('source_url') or 'Not available'}\n"
            f"Stored legal text:\n{result['original_text']}"
            f"{live_reference}"
        )

    async def _build_comparison_context(self, results: list, user_country: str | None) -> str:
        if not self.db:
            return ""

        law_ids = [item["id"] for item in results if item.get("id")]
        if not law_ids:
            return ""

        comparisons = self.db.query(ComparativeLaw).filter(
            or_(
                ComparativeLaw.saudi_law_id.in_(law_ids),
                ComparativeLaw.foreign_law_id.in_(law_ids),
            )
        ).limit(5).all()

        matching = [
            comp for comp in comparisons
            if self._country_matches(comp.foreign_content.country, user_country)
        ]
        if not matching:
            return ""

        parts = [
            "### Tourist country comparison context",
            "Use this section to compare Saudi rules with the tourist's own country when it is relevant.",
        ]
        for idx, comp in enumerate(matching, 1):
            foreign = comp.foreign_content
            saudi = comp.saudi_content
            foreign_live_text = await self.source_fetcher.fetch_text(foreign.source_url)
            parts.append(
                f"Comparison {idx}:\n"
                f"Saudi source: {saudi.country} - {saudi.title}\n"
                f"Saudi text: {saudi.original_text}\n"
                f"Tourist country source: {foreign.country} - {foreign.title}\n"
                f"Tourist country source URL: {foreign.source_url or 'Not available'}\n"
                f"Tourist country stored text: {foreign.original_text}\n"
                f"{f'Tourist country text fetched from source URL: {foreign_live_text}' if foreign_live_text else ''}\n"
                f"Stored comparison summary: {comp.summary}"
            )
        return "\n\n".join(parts)

    def _country_matches(self, source_country: str | None, user_country: str | None) -> bool:
        if not source_country or not user_country:
            return False

        source = self._normalize_country(source_country)
        user = self._normalize_country(user_country)
        if not source or not user or user == "sa":
            return False
        return source == user

    def _normalize_country(self, country: str | None) -> str:
        value = (country or "").strip().lower()
        if not value:
            return ""
        for canonical, aliases in COUNTRY_ALIASES.items():
            if value in aliases:
                return canonical
        return value

    def _display_name(self, user_name: str | None, language: str) -> str:
        fallback = "صديقي" if language == "ar" else "friend"
        if not user_name:
            return fallback
        return user_name.strip().split()[0] or fallback

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
