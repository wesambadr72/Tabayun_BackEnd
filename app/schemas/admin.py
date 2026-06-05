from pydantic import BaseModel, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

# إحصائيات لوحة التحكم
class AdminDashboardStats(BaseModel):
    total_laws: int
    total_countries: int
    total_comparisons: int
    total_users: int
    total_categories: int

# سجل التعديلات (Audit Logs)
class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    action: str
    table_name: str
    record_id: Optional[int]
    old_values: Optional[dict]
    new_values: Optional[dict]
    created_at: datetime
    admin_id: Optional[int] = None
    admin_name: Optional[str] = None

    @field_validator('admin_id', mode='before')
    @classmethod
    def get_admin_id(cls, v: Any, info: Any) -> Any:
        # In from_attributes mode, 'v' is the SQLAlchemy model instance
        if hasattr(v, 'user_id'):
            return v.user_id
        return v

    @field_validator('admin_name', mode='before')
    @classmethod
    def get_admin_name(cls, v: Any, info: Any) -> Any:
        # v is the AuditLog instance
        if hasattr(v, 'user') and v.user:
            return v.user.full_name or v.user.email
        return "Unknown"

    class Config:
        from_attributes = True

# إعدادات النظام والذكاء الاصطناعي
class SystemConfigBase(BaseModel):
    key: str
    value: str
    example_value: Optional[str] = None
    description: Optional[str] = None

class SystemConfigUpdate(BaseModel):
    value: str
    description: Optional[str] = None

class SystemConfigResponse(SystemConfigBase):
    id: int
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# الإشعارات (Admin Notifications)
class AdminNotificationCreate(BaseModel):
    title: str
    content: str
    target_user_ids: Optional[List[int]] = None

class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    target_user_id: Optional[int] = None
    target_user_name: Optional[str] = None
    is_broadcast: bool
    created_at: datetime

    @field_validator('target_user_name', mode='before')
    @classmethod
    def get_target_user_name(cls, v: Any, info: Any) -> Any:
        # info.data contains the model instance when using from_attributes
        # But wait, 'v' is just the value if it exists. 
        # Let's use a simpler approach since we are in Pydantic v2
        return v

    class Config:
        from_attributes = True
