from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.security import get_current_user
from app.db.database import get_db
from app.db.models import Bookmark, ComparativeLaw, User
from app.schemas.user import BookmarkCreate, BookmarkResponse
from app.services.demo_fallback import (
    get_comparison_detail as get_demo_comparison_detail,
    get_priority_comparisons as get_demo_priority_comparisons,
)
from app.services.translation_service import translation_service

router = APIRouter()


@router.get("/priority", response_model=List[dict])
async def get_priority_comparisons(
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = text(
        """
        SELECT
            cl.id AS id,
            lc.title AS title,
            lc.simplified_text AS simplified_description,
            cl.summary AS summary,
            lc.category_id AS category_id,
            fl.country AS foreign_country
        FROM comparative_laws cl
        JOIN legal_contents lc ON cl.saudi_law_id = lc.id
        JOIN legal_contents fl ON cl.foreign_law_id = fl.id
        ORDER BY COALESCE(lc.importance_score, 0) DESC, cl.id DESC
        LIMIT 12
        """
    )

    try:
        result = db.execute(query).fetchall()
        laws = [dict(row._mapping) for row in result]
    except SQLAlchemyError:
        return get_demo_priority_comparisons()

    if (current_user.language == "en" or lang == "en") and lang != "ar":
        laws = await translation_service.translate_comparison_list(laws)

    return laws


@router.post("/bookmark", response_model=BookmarkResponse)
def add_bookmark(
    bookmark_in: BookmarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        comparison = db.query(ComparativeLaw).filter(ComparativeLaw.id == bookmark_in.comparison_id).first()
        if not comparison:
            raise HTTPException(status_code=404, detail="Comparison not found")

        existing = (
            db.query(Bookmark)
            .filter(
                Bookmark.user_id == current_user.id,
                Bookmark.comparison_id == bookmark_in.comparison_id,
            )
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Bookmark already exists")

        new_bookmark = Bookmark(user_id=current_user.id, comparison_id=bookmark_in.comparison_id)
        db.add(new_bookmark)
        db.commit()
        db.refresh(new_bookmark)
        return new_bookmark
    except SQLAlchemyError:
        return {
            "id": bookmark_in.comparison_id,
            "user_id": current_user.id,
            "comparison_id": bookmark_in.comparison_id,
            "created_at": datetime.now(timezone.utc),
        }


@router.get("/bookmarks", response_model=List[dict])
def get_my_bookmarks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        bookmarks = db.query(Bookmark).filter(Bookmark.user_id == current_user.id).all()
        result = []
        for bookmark in bookmarks:
            comp = None
            if bookmark.comparison and bookmark.comparison.saudi_content:
                comp = {
                    "id": bookmark.comparison.id,
                    "title": bookmark.comparison.saudi_content.title,
                    "simplified_description": bookmark.comparison.summary,
                    "category_id": bookmark.comparison.saudi_content.category_id,
                }

            result.append(
                {
                    "id": bookmark.id,
                    "user_id": bookmark.user_id,
                    "comparison_id": bookmark.comparison_id,
                    "created_at": bookmark.created_at,
                    "comparison": comp,
                }
            )
        return result
    except SQLAlchemyError:
        return []


@router.get("/{comparison_id}", response_model=dict)
async def get_comparison_detail(
    comparison_id: int,
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        comparison = db.query(ComparativeLaw).filter(ComparativeLaw.id == comparison_id).first()
        if not comparison:
            raise HTTPException(status_code=404, detail="Comparison not found")

        data = {
            "id": comparison.id,
            "title": comparison.saudi_content.title,
            "saudi_law": {
                "title": comparison.saudi_content.title,
                "text": comparison.saudi_content.simplified_text,
                "source_url": comparison.saudi_content.source_url,
                "article_number": comparison.saudi_content.article_number,
            },
            "foreign_law": {
                "country": comparison.foreign_content.country,
                "title": comparison.foreign_content.title,
                "text": comparison.foreign_content.simplified_text,
                "source_url": comparison.foreign_content.source_url,
                "article_number": comparison.foreign_content.article_number,
            },
            "summary": comparison.summary,
            "category_id": comparison.saudi_content.category_id,
        }
    except SQLAlchemyError:
        data = get_demo_comparison_detail(comparison_id)
        if not data:
            raise HTTPException(status_code=404, detail="Comparison not found")

    if (current_user.language == "en" or lang == "en") and lang != "ar":
        data = await translation_service.translate_comparison_detail(data)

    return data
