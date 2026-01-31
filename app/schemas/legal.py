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
    description: str
    category_id: int
    aria_label: str | None = None
    alt_text: str | None = None
    ui_role: str | None = None
    is_live: int = 0

class LegalContentCreate(LegalContentBase):
    pass

class LegalContent(LegalContentBase):
    id: int

    class Config:
        from_attributes = True

# Comparative Law Schemas
class ComparativeLawBase(BaseModel):
    content_id: int
    saudi_law: str
    foreign_law: str
    key_differences: str | None = None

class ComparativeLawCreate(ComparativeLawBase):
    pass

class ComparativeLaw(ComparativeLawBase):
    id: int

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
