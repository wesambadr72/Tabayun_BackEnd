from pydantic import BaseModel
from datetime import datetime

class NotificationBase(BaseModel):
    recipient_id: int
    title: str
    message: str
    notification_type: str # alert, update, info
    priority: str = "Normal"
    category_id: int | None = None
    scheduled_time: datetime | None = None

class NotificationCreate(NotificationBase):
    sender_id: int | None = None

class Notification(NotificationBase):
    id: int
    sender_id: int | None = None
    status: str = "Unread"
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationConfig(BaseModel):
    user_id: int
    channel: str # Email, SMS, Push
    topics: str # Comma-separated list
    frequency: str = "Daily"
    schedule_time: str | None = None
