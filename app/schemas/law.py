from pydantic import BaseModel
from datetime import datetime

class LawBase(BaseModel):
    title: str
    content: str
    category: str
    country: str

class LawCreate(LawBase):
    pass

class Law(LawBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
