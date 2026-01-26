from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    source: str | None = None
