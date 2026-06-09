import re

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.db.models import ComparativeLaw
from app.services.openai_service import OpenAIService
from app.services.source_fetcher import SourceFetcher
from app.services.vector_search import VectorSearchService

MIN_CHAT_SIMILARITY = 0.4

LEGAL_INTENT_TERMS = (
    "قانون", "نظام", "نظامي", "نظاميه", "قانوني", "قانونيه", "مخالفه",
    "مخالفة", "مخالفات", "عقوبه", "عقوبة", "غرامه", "غرامة", "جزاء",
    "مسموح", "ممنوع", "محظور", "تصريح", "رخصه", "رخصة", "قياده",
    "قيادة", "مرور", "ساهر", "تصوير", "لباس", "احتشام", "تاشيره",
    "تأشيرة", "فيزا", "اقامه", "إقامة", "الاقامة", "الإقامة", "عمل",
    "عامل", "عمال", "محكمه", "محكمة", "شرطه", "شرطة", "سجن", "جريمه",
    "جريمة", "توقيف", "بلاغ", "السعوديه", "السعودية", "بريطانيا",
    "المانيا", "ألمانيا", "traffic", "visa", "residency", "labor", "law",
    "legal", "regulation", "regulations", "fine", "penalty", "violation",
    "allowed", "forbidden", "permit", "license", "driving", "filming",
    "dress", "court", "police", "public decency", "saudi", "ksa",
)

GENERAL_CHAT_TERMS = (
    "السلام", "سلام", "هلا", "اهلا", "أهلا", "مرحبا", "صباح الخير",
    "مساء الخير", "كيفك", "كيف حالك", "كيف الحال", "كيف الامور",
    "كيف الأمور", "كيف", "شكرا", "شكر", "يعطيك العافيه", "يعطيك العافية",
    "مين انت", "من انت", "من أنت", "وش انت", "ايش انت", "ما هو تباين",
    "وش تباين", "ايش تباين", "تباين", "وش تقدر", "ايش تقدر",
    "ماذا تستطيع", "ساعدني", "مساعده", "مساعدة", "hi", "hello", "hey",
    "salam", "thanks", "thank you", "who are you", "what are you",
    "what can you do", "help",
)

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
        intent = await self._resolve_question_intent(question, language)
        if intent == "general":
            return self._general_chat_response(question, language, user_name)
        if intent == "off_topic":
            return self._off_topic_response(language)

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
        result_dict = await self.openai.generate_with_context(
            question,
            context,
            language=language,
            user_name=user_name,
            user_country=user_country,
        )
        
        answer = result_dict.get("answer") if result_dict else None
        sources = self._extract_sources(similar_laws)

        return {
            "answer": answer or (
                "عذرًا، حدث خطأ في معالجة السؤال."
                if language == "ar"
                else "Sorry, an error occurred while processing your question."
            ),
            "sources": sources,
            "context_used": len(similar_laws),
            "is_legal": result_dict.get("is_legal", True) if result_dict else True,
            "has_enough_info": result_dict.get("has_enough_info", True) if result_dict else True,
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
        is_arabic = language.lower() in ["ar", "arabic"]
        fallback = "صديقي" if is_arabic else "friend"
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

    async def _resolve_question_intent(self, question: str, language: str) -> str:
        ai_intent = await self.openai.classify_chat_intent(question, language=language)
        if ai_intent in {"legal", "general", "off_topic"}:
            return ai_intent
        return self._classify_question_intent(question)

    def _classify_question_intent(self, question: str) -> str:
        text = self._normalize_question(question)
        if not text:
            return "general"

        if any(term in text for term in LEGAL_INTENT_TERMS):
            return "legal"

        if self._is_general_chat(text):
            return "general"

        return "off_topic"

    def _normalize_question(self, question: str) -> str:
        text = (question or "").strip().lower()
        replacements = {
            "أ": "ا",
            "إ": "ا",
            "آ": "ا",
            "ى": "ي",
            "ؤ": "و",
            "ئ": "ي",
            "ة": "ه",
        }
        for old, new in replacements.items():
            text = text.replace(old, new)
        text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def _is_general_chat(self, text: str) -> bool:
        if text in GENERAL_CHAT_TERMS:
            return True

        social_terms = (
            "السلام", "سلام", "هلا", "اهلا", "مرحبا", "صباح الخير",
            "مساء الخير", "كيفك", "كيف حالك", "كيف الحال", "كيف الامور",
            "شكرا", "شكر", "يعطيك العافيه", "hi", "hello", "hey", "salam",
            "thanks", "thank you",
        )
        product_terms = (
            "مين انت", "من انت", "من أنت", "وش انت", "ايش انت", "ما هو تباين",
            "وش تباين", "ايش تباين", "وش تقدر", "ايش تقدر", "ماذا تستطيع",
            "who are you", "what are you", "what can you do", "tabayun",
        )

        if len(text.split()) <= 3 and any(term in text for term in social_terms):
            return True
        return any(term in text for term in product_terms)

    def _general_chat_response(
        self,
        question: str,
        language: str,
        user_name: str | None,
    ) -> dict:
        text = self._normalize_question(question)
        display_name = self._display_name(user_name, language)

        if language == "ar":
            if any(term in text for term in ("شكرا", "شكر", "يعطيك العافيه")):
                answer = f"العفو يا {display_name}. أنا موجود إذا احتجت تفهم موقف قانوني أو نظامي بطريقة واضحة."
            elif any(term in text for term in ("مين انت", "من انت", "وش انت", "ايش انت", "تباين", "وش تقدر", "ايش تقدر", "ماذا تستطيع", "ساعدني")):
                answer = (
                    "أنا مساعد تباين. أساعدك تفهم الأنظمة والمواقف القانونية المرتبطة "
                    "بالسياحة والحياة اليومية في السعودية بأسلوب واضح وودّي. اسألني عن "
                    "مخالفة، تصريح، قيادة، تصوير، لباس، إقامة، أو أي موقف قانوني مشابه."
                )
            else:
                answer = (
                    f"يا هلا يا {display_name}. معك تباين، جاهز أساعدك بأسلوب واضح وودّي. "
                    "اكتب لي الموقف أو السؤال القانوني، وبأعطيك خلاصة مفيدة من المصادر المتاحة."
                )
        else:
            if any(term in text for term in ("thanks", "thank you")):
                answer = f"You are welcome, {display_name}. Send me any legal situation when you need a clear explanation."
            elif any(term in text for term in ("who are you", "what are you", "what can you do", "help", "tabayun")):
                answer = (
                    "I am Tabayun's assistant. I help explain legal and everyday regulatory "
                    "situations in Saudi Arabia in a clear, friendly way. Ask about violations, "
                    "permits, driving, filming, dress rules, residency, or similar legal topics."
                )
            else:
                answer = (
                    f"Hi {display_name}. I am Tabayun's assistant, ready to help in a clear and friendly way. "
                    "Send me the legal situation or question and I will summarize what the available sources say."
                )

        return {
            "answer": answer,
            "sources": [],
            "context_used": 0,
            "intent": "general",
        }

    def _off_topic_response(self, language: str) -> dict:
        if language == "ar":
            answer = (
                "هذا خارج نطاق تباين. أقدر أساعدك في الأسئلة القانونية والأنظمة المرتبطة "
                "بالسياحة أو المواقف اليومية في السعودية، مثل المخالفات، التصاريح، القيادة، "
                "التصوير، اللباس، الإقامة، أو قواعد الأماكن العامة."
            )
        else:
            answer = (
                "That is outside Tabayun's scope. I can help with legal and regulatory questions "
                "related to tourism or everyday situations in Saudi Arabia, such as violations, "
                "permits, driving, filming, dress rules, residency, or public-place rules."
            )

        return {
            "answer": answer,
            "sources": [],
            "context_used": 0,
            "intent": "off_topic",
        }
