from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.db.database import get_db
from app.db.models import User, SearchHistory, ComparativeLaw, LegalContent
from app.core.security import get_current_user
from app.services.vector_search import VectorSearchService
from app.schemas.interaction import SearchHistory as SearchHistorySchema
from app.services.translation_service import translation_service

router = APIRouter()

@router.get("/query", response_model=List[dict])
async def search_laws(
    q: str = Query(..., min_length=2, description="كلمات البحث"),
    lang: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    محرك بحث معنوي (Semantic Search) للبحث في القوانين والمقارنات.
    يقوم بالبحث في كافة القوانين وإرجاع النتائج الأكثر صلة ببلد المستخدم.
    """
    vector_search = VectorSearchService(db)
    
    # 1. القيام بالبحث المعنوي
    results = vector_search.search_similar_laws(query_text=q, top_k=10)
    
    law_ids = [item["id"] for item in results]
    
    # Batch fetch all relevant comparisons in a single query (Fixes N+1 issue)
    comparisons = db.query(ComparativeLaw).filter(
        (ComparativeLaw.saudi_law_id.in_(law_ids)) | 
        (ComparativeLaw.foreign_law_id.in_(law_ids))
    ).all()

    # Map comparisons by law_id for fast lookup
    law_to_comp = {}
    for comp in comparisons:
        law_to_comp[comp.saudi_law_id] = comp
        law_to_comp[comp.foreign_law_id] = comp
    
    search_results = []
    
    for item in results:
        law = item["law"]
        comparison = law_to_comp.get(law.id)
        
        if comparison:
            # نتحقق إذا كانت هذه المقارنة تخص بلد المستخدم أو السعودية
            is_relevant = (
                comparison.foreign_content.country == current_user.country or 
                comparison.saudi_content.country == "Saudi Arabia"
            )
            
            if is_relevant:
                search_results.append({
                    "id": comparison.id,
                    "title": comparison.saudi_content.title,
                    "description": comparison.saudi_content.simplified_text,
                    "country": comparison.foreign_content.country,
                    "type": "comparison",
                    "score": item.get('similarity', 0)
                })
    
    # 2. تسجيل عملية البحث في التاريخ (History)
    new_search = SearchHistory(
        user_id=current_user.id,
        keywords=q,
        user_country=current_user.country or "Unknown",
        search_results=json.dumps([{"id": r["id"]} for r in search_results[:5]])
    )
    db.add(new_search)
    db.commit()
    
    # الترجمة فقط إذا كانت لغة المستخدم إنجليزية أو تم طلبها صراحة عبر الرابط
    if (current_user.language == "en" or lang == "en") and lang != "ar":
        search_results = await translation_service.translate_comparison_list(search_results)
        
    return search_results

@router.get("/history", response_model=List[SearchHistorySchema])
def get_search_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """جلب سجل عمليات البحث الخاصة بالمستخدم"""
    return db.query(SearchHistory).filter(SearchHistory.user_id == current_user.id).order_by(SearchHistory.search_time.desc()).limit(10).all()