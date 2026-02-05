from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func, Index, Table, Float
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from app.db.database import Base

# Association table for User-Category subscriptions
subscriptions = Table(
    "subscriptions",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id"), primary_key=True)
)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    country = Column(String, nullable=False)
    language = Column(String, default="Arabic")
    role = Column(String, default="user") # user, admin
    
    # Relationships
    bookmarks = relationship("Bookmark", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")
    searches = relationship("SearchHistory", back_populates="user")
    subscribed_categories = relationship("Category", secondary=subscriptions, back_populates="subscribers")
    settings = relationship("UserSettings", back_populates="user", uselist=False)
    sent_notifications = relationship("Notification", foreign_keys="Notification.sender_id", back_populates="sender")
    received_notifications = relationship("Notification", foreign_keys="Notification.recipient_id", back_populates="recipient")
    support_tickets = relationship("SupportTicket", back_populates="user")

class UserSettings(Base):
    __tablename__ = "user_settings"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    font_size = Column(String, default="medium") # small, medium, large
    font_weight = Column(String, nullable=True)
    line_spacing = Column(String, nullable=True)
    theme_mode = Column(String, default="Light") # Light, Dark
    language = Column(String, default="Arabic")
    fallback_language = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="settings")

class Category(Base):
    """الأقسام القانونية (المرور، التجارة، الصحة...)"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)  # "المرور"
    description = Column(Text, nullable=True)
    icon = Column(String(255), nullable=True)  # path للأيقونة
    
    # Relationships
    contents = relationship("LegalContent", back_populates="category")
    notifications = relationship("Notification", back_populates="category")
    subscribers = relationship("User", secondary=subscriptions, back_populates="subscribed_categories")

class LegalContent(Base):
    """القوانين الفردية (نص واحد من دولة واحدة)"""
    __tablename__ = "legal_contents"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Info
    title = Column(String(300), index=True, nullable=False)  # "مخالفة حزام الأمان"
    country = Column(String(50), index=True, nullable=False)  # "السعودية"
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Legal Texts
    original_text = Column(Text, nullable=False)      # النص القانوني الأصلي من الموقع
    simplified_text = Column(Text, nullable=False)    # النص المبسط بواسطة AI
    
    # Metadata
    source_url = Column(String(500), nullable=True)   # رابط المصدر (WorldLII)
        
    # Vector Search
    embedding = Column(Vector(384), nullable=True)    # 384 إذا استخدمت sentence-transformers
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Accessibility
    aria_label = Column(String(255), nullable=True)
    alt_text = Column(String(255), nullable=True)
    ui_role = Column(String(50), nullable=True)
    is_live = Column(Integer, default=0)
    
    # Relationships
    category = relationship("Category", back_populates="contents")
    saudi_comparisons = relationship(
        "ComparativeLaw",
        foreign_keys="ComparativeLaw.saudi_law_id",
        back_populates="saudi_content"
    )
    foreign_comparisons = relationship(
        "ComparativeLaw",
        foreign_keys="ComparativeLaw.foreign_law_id",
        back_populates="foreign_content"
    )
    bookmarks = relationship("Bookmark", back_populates="content")


class ComparativeLaw(Base):
    """المقارنات بين السعودية ودول أخرى"""
    __tablename__ = "comparative_laws"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # References (بدلاً من تكرار النصوص)
    saudi_law_id = Column(Integer, ForeignKey("legal_contents.id"), nullable=False)
    foreign_law_id = Column(Integer, ForeignKey("legal_contents.id"), nullable=False)
    
    # Summary (الخلاصة التوضيحية - جملة واحدة)
    summary = Column(Text, nullable=False)  # "الكحول محرم في السعودية ومسموح في ألمانيا بشرط..."
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    saudi_content = relationship(
        "LegalContent",
        foreign_keys=[saudi_law_id],
        back_populates="saudi_comparisons"
    )
    foreign_content = relationship(
        "LegalContent",
        foreign_keys=[foreign_law_id],
        back_populates="foreign_comparisons"
    )
    
    # Unique constraint: نفس المقارنة لا تتكرر
    __table_args__ = (
        Index('idx_comparison_pair', 'saudi_law_id', 'foreign_law_id', unique=True),
    )


class Bookmark(Base):
    """علامات مرجعية للمستخدمين"""
    __tablename__ = "bookmarks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("legal_contents.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="bookmarks")
    content = relationship("LegalContent", back_populates="bookmarks")

class Feedback(Base):
    __tablename__ = "feedbacks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="feedbacks")

class SearchHistory(Base):
    __tablename__ = "search_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    keywords = Column(String, nullable=False)
    user_country = Column(String, nullable=False)
    search_results = Column(Text, nullable=True)
    search_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="searches")

class AIChatbot(Base):
    __tablename__ = "ai_chatbot"
    id = Column(Integer, primary_key=True, index=True)
    training_data = Column(Text, nullable=True)
    version = Column(String, nullable=False)
    response_templates = Column(Text, nullable=True)
    timeout_limit = Column(Integer, default=10)
    legal_data = Column(Text, nullable=True)
    response_time = Column(Float, nullable=True)
    error_rate = Column(Float, nullable=True)

class LoginHistory(Base):
    __tablename__ = "login_history"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    login_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String, default="Success")

class SupportTicket(Base):
    __tablename__ = "support_tickets"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    category = Column(String, nullable=False) # Technical, General, etc
    message = Column(Text, nullable=False)
    attachments = Column(String, nullable=True) # File URLs
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="support_tickets")

class AboutUs(Base):
    __tablename__ = "about_us"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False) # About, Team, Mission
    body = Column(Text, nullable=False)
    image_url = Column(String, nullable=True)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
