from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db.models import Category, LegalContent, User, Notification
from app.schemas.legal import Category as CategorySchema, LegalContent as LegalContentSchema
from app.core.security import get_current_user

router = APIRouter()

@router.get("/categories", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    """جلب قائمة الأقسام"""
    return db.query(Category).all()

@router.get("/countries", response_model=List[str])
def get_available_countries(db: Session = Depends(get_db)):
    """جلب قائمة بجميع الدول المتاحة في القوانين"""
    # جلب الدول من جدول القوانين
    countries = db.query(LegalContent.country).filter(LegalContent.country != "sa").distinct().all()
    #  تحويل القائمة من مصفوفة Tuple إلى مصفوفة Strings بسيطة
    return [c[0] for c in countries if c[0]]

@router.get("/by-category/{category_id}", response_model=List[dict])
def get_laws_by_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """جلب قوانين بلد المستخدم الذهبية (الحقول الأساسية فقط)"""
    
    # استعلام لجلب القوانين من الـ View مع تصفية حسب القسم وبلد المستخدم
    query = text("""
        SELECT id, title, simplified_text, country, category_id, saudi_reference_id, source_url, article_number 
        FROM priority_legal_contents 
        WHERE category_id = :cat_id 
        AND country = :country
    """)
    
    result = db.execute(query, {"cat_id": category_id, "country": current_user.country}).fetchall()
    return [dict(row._mapping) for row in result]

@router.post("/subscribe/{category_id}")
def subscribe_to_category(
    category_id: int, 
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """تفعيل/إلغاء الجرس لمتابعة قسم معين"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    if category in current_user.subscribed_categories:
        current_user.subscribed_categories.remove(category)
        message = "Unsubscribed successfully"
    else:
        current_user.subscribed_categories.append(category)
        message = "Subscribed successfully"
    
    db.commit()
    return {"message": message}

@router.get("/my-notifications")
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """جلب قائمة الإشعارات الخاصة بالمستخدم (الجرس)"""
    # جلب الإشعارات الخاصة به أو الإشعارات العامة (Broadcast)
    try:
        notifications = db.query(Notification).filter(
            (Notification.recipient_id == current_user.id) | (Notification.is_broadcast == True)
        ).order_by(Notification.created_at.desc()).all()
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))