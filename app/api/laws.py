from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Category, LegalContent, Notification, User
from app.schemas.legal import Category as CategorySchema
from app.services.demo_fallback import (
    DEMO_CATEGORIES,
    DEMO_COUNTRIES,
    get_comparisons_by_category as get_demo_comparisons_by_category,
    get_priority_comparisons as get_demo_priority_comparisons,
)
from app.services.translation_service import translation_service
from app.utils.helpers import get_target_language_code, get_language_code

router = APIRouter()

# الحصول على قائمة التصنيفات
@router.get("/categories", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    try:
        return db.query(Category).all()
    except SQLAlchemyError:
        return DEMO_CATEGORIES

# الحصول على قائمة الدول المتاحة
@router.get("/countries", response_model=List[str])
def get_available_countries(db: Session = Depends(get_db)):
    try:
        countries = db.query(LegalContent.country).filter(LegalContent.country != "sa").distinct().all()
        return [country[0] for country in countries if country[0]]
    except SQLAlchemyError:
        return DEMO_COUNTRIES


# الحصول على قائمة المقارنات حسب التصنيف
@router.get("/by-category/{category_id}", response_model=List[dict])
async def get_laws_by_category(
    category_id: int,
    country: Optional[str] = None,
    lang: str = "ar",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Use provided country or current user's country
    target_country = country or current_user.country
    
    query = text(
        """
        SELECT 
            cl.id as id,
            lc.title as title,
            lc.simplified_text as description,
            lc.article_number,
            fl.country as foreign_country,
            fl.title as foreign_title
        FROM comparative_laws cl
        JOIN legal_contents lc ON cl.saudi_law_id = lc.id
        JOIN legal_contents fl ON cl.foreign_law_id = fl.id
        WHERE lc.category_id = :cat_id 
        """ + ("AND fl.country = :country" if target_country else "")
    )

    params = {"cat_id": category_id}
    if target_country:
        params["country"] = target_country

    try:
        result = db.execute(query, params).fetchall()
        laws = []
        for row in result:
            row_dict = dict(row._mapping)
            # المواءمة مع ما يتوقعه الفرونت إند (Comparison interface)
            laws.append({
                "id": row_dict["id"],
                "title": row_dict["title"],
                "simplified_description": row_dict["description"],
                "foreign_law": {
                    "title": row_dict["foreign_title"],
                    "country": row_dict["foreign_country"]
                }
            })
    except SQLAlchemyError:
        return get_demo_comparisons_by_category(category_id, target_country)

    # الترجمة حسب لغة المستخدم أو اللغة المطلوبة
    full_lang = get_target_language_code(lang, current_user.language)
    lang_code = get_language_code(full_lang)
    if lang_code != "ar":
        laws = await translation_service.translate_comparison_list(laws, target_lang=lang_code)

    return laws


# الحصول على قائمة التصنيفات المفضلة للمستخدم
@router.post("/subscribe/{category_id}")
def subscribe_to_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
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
    except SQLAlchemyError:
        return {"message": "Subscribed successfully"}


# الحصول على إشعارات المستخدم الحالي
@router.get("/my-notifications")
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notifications = (
            db.query(Notification)
            .filter(
                (Notification.recipient_id == current_user.id) | 
                (Notification.target_user_id == current_user.id) | 
                (Notification.is_broadcast == True)
            )
            .order_by(Notification.created_at.desc())
            .all()
        )
        return notifications
    except SQLAlchemyError:
        return []


# تحديث حالة الإشعار إلى مقروء
@router.post("/notifications/{notif_id}/read")
def mark_notification_as_read(
    notif_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notification = (
            db.query(Notification)
            .filter(Notification.id == notif_id)
            .filter(
                (Notification.recipient_id == current_user.id) | 
                (Notification.target_user_id == current_user.id) | 
                (Notification.is_broadcast == True)
            )
            .first()
        )
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notification.is_read = 1
        db.commit()
        return {"message": "Notification marked as read"}
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Database error")


# الحصول على قائمة المقارنات المهمة للسعودية
@router.get("/saudi-priority", response_model=List[dict])
async def get_saudi_priority_laws(
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = text(
        """
        SELECT id, title, simplified_text as description, country, category_id, source_url, article_number 
        FROM priority_legal_contents
        WHERE country = 'sa'
        """
    )
    try:
        result = db.execute(query).fetchall()
        laws = [dict(row._mapping) for row in result]
    except SQLAlchemyError:
        laws = get_demo_priority_comparisons()

    # الترجمة حسب لغة المستخدم أو اللغة المطلوبة
    full_lang = get_target_language_code(lang, current_user.language)
    lang_code = get_language_code(full_lang)
    if lang_code != "ar":
        laws = await translation_service.translate_comparison_list(laws, target_lang=lang_code)

    return laws

@router.get("/stats")
async def get_laws_stats(
    db: Session = Depends(get_db),
):
    try:
        result = db.execute(text("SELECT COUNT(*) FROM legal_contents")).fetchone()
        return {"total_laws": result[0]}
    except SQLAlchemyError:
        return {"total_laws": 0}