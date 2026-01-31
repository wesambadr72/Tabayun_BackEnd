from pydantic import BaseModel
from datetime import datetime

# Bookmark Schemas
class BookmarkBase(BaseModel):
    user_id: int
    content_id: int

class BookmarkCreate(BookmarkBase):
    pass

class Bookmark(BookmarkBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Feedback Schemas
class FeedbackBase(BaseModel):
    user_id: int
    message: str

class FeedbackCreate(FeedbackBase):
    pass

class Feedback(FeedbackBase):
    id: int
    date: datetime

    class Config:
        from_attributes = True

# Search Schemas
class SearchBase(BaseModel):
    user_id: int
    keywords: str
    user_country: str

class SearchCreate(SearchBase):
    pass

class SearchHistory(SearchBase):
    id: int
    search_results: str | None = None
    search_time: datetime

    class Config:
        from_attributes = True

# Support Ticket Schemas (Table 68)
class SupportTicketBase(BaseModel):
    user_id: int
    category: str
    message: str
    attachments: str | None = None

class SupportTicketCreate(SupportTicketBase):
    pass

class SupportTicket(SupportTicketBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# About Us Schemas (Table 69)
class AboutUsBase(BaseModel):
    title: str
    body: str
    image_url: str | None = None

class AboutUsCreate(AboutUsBase):
    pass

class AboutUs(AboutUsBase):
    id: int
    last_updated: datetime

    class Config:
        from_attributes = True
