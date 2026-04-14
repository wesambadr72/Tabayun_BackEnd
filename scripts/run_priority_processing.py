import asyncio
import sys
import os
from sqlalchemy import text

# إضافة مسار المشروع الرئيسي
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LegalContent, ComparativeLaw # تمت إضافة الاستيراد هنا
from app.services.ai_processor.simplifier_gemini import LawSimplifier
from app.services.ai_processor.comparator_gemini import LawComparator

async def process_priority_laws():
    db = SessionLocal()
    simplifier = LawSimplifier()
    comparator = LawComparator()
    
    print("📡 Fetching priority laws from View...")
    query = text("SELECT id, country, saudi_reference_id FROM priority_legal_contents")
    priority_laws = db.execute(query).fetchall()
    
    total = len(priority_laws)
    print(f"✅ Found {total} laws to process (Simplified + Comparative).")
    print("-" * 50)

    for i, row in enumerate(priority_laws):
        law_id = row.id
        country = row.country
        saudi_ref_id = row.saudi_reference_id
        
        # جلب المادة من قاعدة البيانات للتحقق من حالتها
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law: continue

        print(f"[{i+1}/{total}] Checking Law ID: {law_id} ({country})...")
        
        try:
            # 1. التبسيط (فقط إذا لم تكن مبسطة مسبقاً)
            if not law.simplified_text or law.simplified_text.strip() == "":
                print(f"   ✨ Simplifying...")
                await simplifier.simplify(law_id, db)
            else:
                print(f"   ✅ Already simplified, skipping.")
            
            # 2. المقارنة (فقط إذا كانت مادة أجنبية ولها مرجع سعودي ولم تقارن مسبقاً)
            if country != 'sa' and saudi_ref_id:
                existing_comp = db.query(ComparativeLaw).filter(
                    ComparativeLaw.saudi_law_id == saudi_ref_id,
                    ComparativeLaw.foreign_law_id == law_id
                ).first()
                
                if not existing_comp:
                    print(f"   🔄 Comparing with Saudi Law {saudi_ref_id}...")
                    await comparator.compare_by_ids(saudi_ref_id, law_id, db)
                else:
                    print(f"   ✅ Comparison already exists, skipping.")
                
            # احترام حد الـ RPM
            await asyncio.sleep(1) 
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            continue

    print("-" * 50)
    print(f"🎉 All {total} priority laws simplified and matched successfully!")
    db.close()

if __name__ == "__main__":
    asyncio.run(process_priority_laws())