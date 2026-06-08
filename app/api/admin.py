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
    AdminNotificationCreate, NotificationResponse
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

# --- جلب القوائم (Listing Endpoints) ---

@router.get("/laws", response_model=List[LegalContentSchema])
def list_laws(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    category_id: Optional[int] = None
):
    """جلب قائمة القوانين مع البحث والفلترة حسب القسم"""
    return AdminService.get_all_laws(db, skip, limit, search, category_id)

@router.get("/users", response_model=List[UserResponse])
def list_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None
):
    """جلب قائمة المستخدمين مع البحث"""
    return AdminService.get_all_users(db, skip, limit, search)

@router.get("/configs", response_model=List[SystemConfigResponse])
def list_configs(
    db: Session = Depends(get_db)
):
    """جلب كافة إعدادات النظام"""
    return AdminService.get_all_configs(db)

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

@router.get("/laws/{law_id}", response_model=LegalContentSchema)
def get_law(
    law_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """جلب تفاصيل قانون واحد"""
    law = AdminService.get_law_by_id(db, law_id)
    if not law:
        raise HTTPException(status_code=404, detail="Law not found")
    return law

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

@router.post("/laws/bulk-delete")
def bulk_delete_laws(
    law_ids: List[int],
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """حذف مجموعة قوانين"""
    count = AdminService.bulk_delete_laws(db, current_admin.id, law_ids)
    return {"message": f"Successfully deleted {count} laws"}

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

@router.post("/users/bulk-delete")
def bulk_delete_users(
    user_ids: List[int],
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """حذف مجموعة مستخدمين"""
    count = AdminService.bulk_delete_users(db, current_admin.id, user_ids)
    return {"message": f"Successfully deleted {count} users"}

# --- الإشعارات (Notifications) ---

@router.get("/notifications", response_model=List[NotificationResponse])
def get_all_notifications(
    db: Session = Depends(get_db),
    limit: int = 100,
    offset: int = 0
):
    """جلب كافة الإشعارات المرسلة من قبل الآدمن"""
    notifications = db.query(NotificationModel).order_by(NotificationModel.created_at.desc()).limit(limit).offset(offset).all()
    
    # تحويل البيانات لإضافة اسم المستخدم يدوياً إذا لزم الأمر
    result = []
    for n in notifications:
        n_dict = {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "target_user_id": n.target_user_id,
            "target_user_name": n.target_user.full_name if n.target_user else None,
            "is_broadcast": n.is_broadcast,
            "created_at": n.created_at
        }
        result.append(n_dict)
        
    return result

@router.delete("/notifications/{notif_id}")
def delete_notification(
    notif_id: int,
    db: Session = Depends(get_db)
):
    """حذف إشعار مرسل"""
    notif = db.query(NotificationModel).filter(NotificationModel.id == notif_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    db.delete(notif)
    db.commit()
    return {"message": "Notification deleted successfully"}

@router.post("/notifications/bulk-delete")
def bulk_delete_notifications(
    notif_ids: List[int],
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """حذف مجموعة إشعارات مرسلة"""
    notifs = db.query(NotificationModel).filter(NotificationModel.id.in_(notif_ids)).all()
    deleted_count = 0
    for notif in notifs:
        db.delete(notif)
        deleted_count += 1
    db.commit()
    return {"message": f"Successfully deleted {deleted_count} notifications"}

@router.post("/notifications")
async def send_notification(
    notif_in: AdminNotificationCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(check_admin)
):
    """إرسال إشعار لمستخدم أو مجموعة أو للجميع"""
    if notif_in.target_user_ids and len(notif_in.target_user_ids) > 0:
        # إرسال لمجموعة مستخدمين
        for user_id in notif_in.target_user_ids:
            AdminService.send_notification(
                db, current_admin.id, notif_in.title, notif_in.content, user_id
            )
    else:
        # إشعار عام (Broadcast)
        await NotificationService.send_broadcast_notification(db, notif_in.title, notif_in.content)
    
    return {"message": "Notification sent successfully"}
