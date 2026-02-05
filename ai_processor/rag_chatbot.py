from typing import Optional


class RAGChatbot:
    def __init__(self, embedding_model: Optional[str] = None):
        self.embedding_model = embedding_model

    def answer(self, question: str) -> str:
        return ""

