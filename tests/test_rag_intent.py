from app.core.rag import RAGPipeline
import asyncio


class FakeIntentService:
    def __init__(self, intent):
        self.intent = intent

    async def classify_chat_intent(self, question: str, language: str = "ar"):
        return self.intent


def test_chat_intent_routes_general_messages_without_rag():
    pipeline = RAGPipeline.__new__(RAGPipeline)

    assert pipeline._classify_question_intent("كيف") == "general"
    assert pipeline._classify_question_intent("السلام عليكم") == "general"
    assert pipeline._classify_question_intent("what can you do") == "general"


def test_chat_intent_routes_legal_messages_to_rag():
    pipeline = RAGPipeline.__new__(RAGPipeline)

    assert pipeline._classify_question_intent("هل التصوير في الاماكن العامة مسموح؟") == "legal"
    assert pipeline._classify_question_intent("كيف اطلع رخصة قيادة؟") == "legal"
    assert pipeline._classify_question_intent("food regulations in saudi") == "legal"


def test_chat_intent_rejects_external_topics():
    pipeline = RAGPipeline.__new__(RAGPipeline)

    assert pipeline._classify_question_intent("كيف اطبخ كبسة؟") == "off_topic"
    assert pipeline._classify_question_intent("اكتب لي قصيدة") == "off_topic"
    assert pipeline._classify_question_intent("what is your favorite food") == "off_topic"


def test_ai_intent_router_takes_priority():
    pipeline = RAGPipeline.__new__(RAGPipeline)
    pipeline.openai = FakeIntentService("off_topic")

    intent = asyncio.run(pipeline._resolve_question_intent("is filming allowed?", "en"))

    assert intent == "off_topic"


def test_ai_intent_router_falls_back_when_unavailable():
    pipeline = RAGPipeline.__new__(RAGPipeline)
    pipeline.openai = FakeIntentService(None)

    intent = asyncio.run(pipeline._resolve_question_intent("is filming allowed?", "en"))

    assert intent == "legal"
