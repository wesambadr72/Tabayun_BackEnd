import asyncio
import os
import sys

# إضافة المجلد الرئيسي للمسار لضمان عمل الاستيرادات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import LegalContent
from app.services.ai_processor.simplifier_gemini import LawSimplifier
from app.db.views import create_priority_laws_view

async def process_specific_laws():
    db = SessionLocal()
    law_ids = [907]
    simplifier = LawSimplifier()
    
    print(f"--- start processing {law_ids} ---")
    
    for law_id in law_ids:
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law:
            print(f"❌ law with id {law_id} not found in database.")
            continue
            
        print(f"🔄 processing law with id {law_id}: {law.title}...")
        
        # 1. تنفيذ Gemini
        result = await simplifier.simplify(law_id, db)
        
        if "error" in result:
            print(f"⚠️ error processing law with id {law_id}: {result['error']}")
        else:
            print(f"✅ law with id {law_id} processed successfully.")
            
            # 2. رفعه للأولوية لضمان ظهوره في ال View
            law.importance_score = 10
            # التأكد من أنه نشط
            law.is_live = 1
            
            db.commit()
            print(f"⭐ law with id {law_id} marked as priority (importance score: 10).")

    db.close()
if __name__ == "__main__":
    asyncio.run(process_specific_laws())
