from typing import Optional
from pydantic import BaseModel
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    name: str

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int

    class Config:
        from_attributes = True

# Legal Content Schemas
class LegalContentBase(BaseModel):
    title: str
    country: str
    category_id: int
    original_text: Optional[str] = None
    simplified_text: str
    article_number: Optional[str] = None
    source_url: Optional[str] = None
    importance_score: int = 0
    importance_reason: Optional[str] = None
    is_live: int = 0
    aria_label: Optional[str] = None
    alt_text: Optional[str] = None
    ui_role: Optional[str] = None

class LegalContentCreate(LegalContentBase):
    pass

class LegalContent(LegalContentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Comparative Law Schemas
class ComparativeLawBase(BaseModel):
    saudi_law_id: int
    foreign_law_id: int
    summary: str

class ComparativeLawCreate(ComparativeLawBase):
    pass

class ComparativeLaw(ComparativeLawBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Special Schemas for Display (Tables 52, 53)
class LegalTopicDisplay(BaseModel):
    topic_id: int
    user_country: str
    user_language: str
    legal_topics: str
    category_list: str

class ComprehensiveLawDisplay(BaseModel):
    comparison_id: int
    selected_topic: str
    user_country: str
    saudi_law: str
    home_country_law: str
    comparative_analysis: str | None = None
