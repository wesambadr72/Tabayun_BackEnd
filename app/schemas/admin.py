from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

# إحصائيات لوحة التحكم
class AdminDashboardStats(BaseModel):
    total_laws: int
    total_countries: int
    total_comparisons: int
    total_users: int

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
    target_user_id: Optional[int] = None
