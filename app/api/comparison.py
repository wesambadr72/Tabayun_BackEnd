from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db.models import User, ComparativeLaw, Bookmark
from app.services.ai_processor.comparator_gemini import LawComparator
from app.schemas.user import BookmarkCreate, BookmarkResponse
from app.core.security import get_current_user

router = APIRouter()

@router.get("/priority", response_model=List[dict])
def get_priority_comparisons(db: Session = Depends(get_db)):
    """جلب قائمة المقارنات الذهبية (الحقول الأساسية فقط)"""
    # جلب الحقول التي تهم الواجهة فقط
    query = text("""
        SELECT id, title, simplified_text, country, category_id, saudi_reference_id, source_url, article_number 
        FROM priority_legal_contents
    """)
    result = db.execute(query).fetchall()
    return [dict(row._mapping) for row in result]

@router.post("/bookmark", response_model=BookmarkResponse)
def add_bookmark(
    bookmark_in: BookmarkCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """حفظ مقارنة في المفضلة"""
    # التأكد من وجود المقارنة
    comparison = db.query(ComparativeLaw).filter(ComparativeLaw.id == bookmark_in.comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    # التأكد من عدم وجودها مسبقاً للمستخدم
    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.comparison_id == bookmark_in.comparison_id
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bookmark already exists")

    new_bookmark = Bookmark(
        user_id=current_user.id,
        comparison_id=bookmark_in.comparison_id
    )
    db.add(new_bookmark)
    db.commit()
    db.refresh(new_bookmark)
    return new_bookmark

@router.get("/bookmarks", response_model=List[dict])
def get_my_bookmarks(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """جلب قائمة المفضلة الخاصة بالمستخدم"""
    bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
    result = []
    for b in bookmarks:
        comp = None
        if b.comparison and b.comparison.saudi_content:
            comp = {
                "id": b.comparison.id,
                "title": b.comparison.saudi_content.title,
                "simplified_description": b.comparison.summary,
                "category_id": b.comparison.saudi_content.category_id
            }
        
        result.append({
            "id": b.id,
            "user_id": b.user_id,
            "comparison_id": b.comparison_id,
            "created_at": b.created_at,
            "comparison": comp
        })
    return result

@router.get("/{comparison_id}", response_model=dict)
def get_comparison_detail(
    comparison_id: int, 
    db: Session = Depends(get_db)
):
    """جلب تفاصيل المقارنة الكاملة (للعرض في كرت المقارنة)"""
    comparison = db.query(ComparativeLaw).filter(ComparativeLaw.id == comparison_id).first()
    if not comparison:
        raise HTTPException(status_code=404, detail="Comparison not found")
    
    return {
        "id": comparison.id,
        "title": comparison.saudi_content.title,
        "saudi_law": {
            "title": comparison.saudi_content.title,
            "text": comparison.saudi_content.simplified_text,
            "source_url": comparison.saudi_content.source_url,
            "article_number": comparison.saudi_content.article_number
        },
        "foreign_law": {
            "country": comparison.foreign_content.country,
            "title": comparison.foreign_content.title,
            "text": comparison.foreign_content.simplified_text,
            "source_url": comparison.foreign_content.source_url,
            "article_number": comparison.foreign_content.article_number
        },
        "summary": comparison.summary,
        "category_id": comparison.saudi_content.category_id
    }
