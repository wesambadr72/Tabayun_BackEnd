from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from app.db.database import get_db
from app.db.models import User, LegalContent, Notification as NotificationModel
from app.services.admin_service import AdminService
from app.services.notification_service import NotificationService
from app.schemas.admin import (
    AdminDashboardStats, AuditLogResponse, 
    SystemConfigResponse, SystemConfigUpdate,
    AdminNotificationCreate
)
from app.schemas.user import UserResponse
from app.schemas.legal import LegalContent as LegalContentSchema, LegalContentCreate
from app.core.security import get_current_user, check_admin

router = APIRouter(dependencies=[Depends(check_admin)])

@router.get("/stats", response_model=AdminDashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db)
):
    """جلب إحصائيات لوحة التحكم"""
    return AdminService.get_dashboard_stats(db)

# --- إدارة التاريخ والتعديلات ---
@router.get("/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db), 
    limit: int = 100,
    offset: int = 0
):
    """جلب تاريخ التعديلات والرقابة"""
    return AdminService.get_audit_logs(db, limit, offset)

# --- إدارة اعدادات النظام  ---
@router.post("/config", response_model=SystemConfigResponse)
def update_system_config(
    key: str, 
    value: str, 
    example_value: Optional[str] = None,
    description: Optional[str] = None,
    db: Session = Depends(get_db), 
    current_admin: User = Depends(check_admin)
):
    """تعديل إعدادات النظام والذكاء الاصطناعي"""
    return AdminService.update_system_config(db, current_admin.id, key, value, example_value, description)

@router.post("/seed-configs")
def seed_configs(
    db: Session = Depends(get_db), 
    current_admin: User = Depends(check_admin)
):
    """إدخال الإعدادات الافتراضية للنظام (تشغيل مرة واحدة)"""
    AdminService.seed_default_configs(db, current_admin.id)
    return {"message": "Default configs seeded successfully"}

# --- إدارة القوانين (Laws CRUD) ---

@router.post("/laws", response_model=LegalContentSchema)
async def add_law(
    law_in: LegalContentCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """إضافة قانون جديد"""
    try:
        return await AdminService.add_law(db, current_admin.id, law_in.model_dump())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/laws/{law_id}", response_model=LegalContentSchema)
def update_law(
    law_id: int,
    law_in: Dict[str, Any],
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """تعديل قانون موجود"""
    law = AdminService.update_law(db, current_admin.id, law_id, law_in)
    if not law:
        raise HTTPException(status_code=404, detail="Law not found")
    return law

@router.delete("/laws/{law_id}")
def delete_law(
    law_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """حذف قانون"""
    success = AdminService.delete_law(db, current_admin.id, law_id)
    if not success:
        raise HTTPException(status_code=404, detail="Law not found")
    return {"message": "Law deleted successfully"}

# --- إدارة المستخدمين (User Management) ---

@router.put("/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    new_role: str,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """تعديل صلاحية مستخدم"""
    try:
        user = AdminService.update_user_role(db, current_admin.id, user_id, new_role)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """حذف مستخدم"""
    success = AdminService.delete_user(db, current_admin.id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}

# --- الإشعارات (Notifications) ---

@router.post("/notifications")
async def send_notification(
    notif_in: AdminNotificationCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """إرسال إشعار لمستخدم أو للجميع"""
    if notif_in.target_user_id:
        # إشعار خاص
        AdminService.send_notification(
            db, current_admin.id, notif_in.title, notif_in.content, notif_in.target_user_id
        )
    else:
        # إشعار عام (Broadcast)
        await NotificationService.send_broadcast_notification(db, notif_in.title, notif_in.content)
    
    return {"message": "Notification sent successfully"}
