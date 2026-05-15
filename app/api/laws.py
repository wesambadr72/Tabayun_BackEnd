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

router = APIRouter()


@router.get("/categories", response_model=List[CategorySchema])
def get_categories(db: Session = Depends(get_db)):
    try:
        return db.query(Category).all()
    except SQLAlchemyError:
        return DEMO_CATEGORIES


@router.get("/countries", response_model=List[str])
def get_available_countries(db: Session = Depends(get_db)):
    try:
        countries = db.query(LegalContent.country).filter(LegalContent.country != "sa").distinct().all()
        return [country[0] for country in countries if country[0]]
    except SQLAlchemyError:
        return DEMO_COUNTRIES


@router.get("/by-category/{category_id}", response_model=List[dict])
async def get_laws_by_category(
    category_id: int,
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = text(
        """
        SELECT 
            cl.id as id,
            lc.title as title,
            lc.simplified_text as description,
            lc.article_number
        FROM comparative_laws cl
        JOIN legal_contents lc ON cl.saudi_law_id = lc.id
        JOIN legal_contents fl ON cl.foreign_law_id = fl.id
        WHERE lc.category_id = :cat_id 
        AND fl.country = :country
        """
    )

    try:
        result = db.execute(query, {"cat_id": category_id, "country": current_user.country}).fetchall()
        laws = [dict(row._mapping) for row in result]
    except SQLAlchemyError:
        return get_demo_comparisons_by_category(category_id, getattr(current_user, "country", None))

    if (current_user.language == "en" or lang == "en") and lang != "ar":
        laws = await translation_service.translate_comparison_list(laws)

    return laws


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


@router.get("/my-notifications")
def get_my_notifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        notifications = (
            db.query(Notification)
            .filter((Notification.recipient_id == current_user.id) | (Notification.is_broadcast == True))
            .order_by(Notification.created_at.desc())
            .all()
        )
        return notifications
    except SQLAlchemyError:
        return []


@router.get("/saudi-priority", response_model=List[dict])
def get_saudi_priority_laws(
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
        return [dict(row._mapping) for row in result]
    except SQLAlchemyError:
        return get_demo_priority_comparisons()
