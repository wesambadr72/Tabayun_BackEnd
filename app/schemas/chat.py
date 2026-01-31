from pydantic import BaseModel
from datetime import datetime

class ChatBase(BaseModel):
    user_query: str

class ChatCreate(ChatBase):
    pass

class ChatResponse(ChatBase):
    chat_id: int
    ai_response: str
    legal_data: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True

class BotManagement(BaseModel):
    bot_id: int
    response_templates: str | None = None
    timeout_limit: int = 10
    legal_data: str | None = None
    response_time: float | None = None
    error_rate: float | None = None

    class Config:
        from_attributes = True

# Legacy support or simplified messages
class ChatMessage(BaseModel):
    message: str

class SimpleChatResponse(BaseModel):
    response: str
    source: str | None = None
