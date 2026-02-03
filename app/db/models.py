from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Float, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
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
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    
    # Relationships
    contents = relationship("LegalContent", back_populates="category")
    notifications = relationship("Notification", back_populates="category")
    subscribers = relationship("User", secondary=subscriptions, back_populates="subscribed_categories")

class LegalContent(Base):
    __tablename__ = "legal_contents"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    country = Column(String, index=True, nullable=False) # الدولة التي يتبع لها القانون
    category_id = Column(Integer, ForeignKey("categories.id"))
    embedding = Column(Vector(1536)) # Vector embedding for semantic search
    
    # Accessibility fields (Table 66)
    aria_label = Column(String, nullable=True)
    alt_text = Column(String, nullable=True)
    ui_role = Column(String, nullable=True)
    is_live = Column(Integer, default=0) # 0 or 1
    
    # Relationships
    category = relationship("Category", back_populates="contents")
    comparisons = relationship("ComparativeLaw", back_populates="content")
    bookmarks = relationship("Bookmark", back_populates="content")

class ComparativeLaw(Base):
    __tablename__ = "comparative_laws"
    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("legal_contents.id"))
    saudi_law = Column(Text, nullable=False)
    foreign_law = Column(Text, nullable=False)
    key_differences = Column(Text, nullable=True)
    embedding = Column(Vector(1536)) # Vector embedding for semantic search
    
    # Relationships
    content = relationship("LegalContent", back_populates="comparisons")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False) # alert, update, info
    priority = Column(String, default="Normal")
    status = Column(String, default="Unread")
    scheduled_time = Column(DateTime, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    category = relationship("Category", back_populates="notifications")
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_notifications")
    recipient = relationship("User", foreign_keys=[recipient_id], back_populates="received_notifications")

class Bookmark(Base):
    __tablename__ = "bookmarks"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content_id = Column(Integer, ForeignKey("legal_contents.id"))
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
