from app.core.rag import RAGPipeline
from sqlalchemy.orm import Session

class RAGChatbot:
    """مساعد قانوني ذكي يعتمد على تقنية RAG للإجابة على الأسئلة"""
    
    def __init__(self, db: Session):
        self.pipeline = RAGPipeline(db)

    async def ask(
        self,
        question: str,
        country_filter: str = None,
        language: str = "ar",
        user_name: str | None = None,
        user_country: str | None = None,
    ) -> dict:
        """
        الإجابة على سؤال المستخدم باستخدام الـ RAG Pipeline الموحد.
        """
        return await self.pipeline.answer_question(
            question=question,
            country_filter=country_filter,
            language=language,
            user_name=user_name,
            user_country=user_country,
        )
