import asyncio
import os
import sys

# إضافة المجلد الرئيسي للمسار لضمان عمل الاستيرادات
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.services.ai_processor.comparator_gemini import LawComparator

async def batch_compare():
    db = SessionLocal()
    comparator = LawComparator()
    
    # قائمة المقارنات (saudi_law_id, foreign_law_id)
    pairs = [
        (163, 1416), (391, 1331), (397, 1403)
    ]
    
    print(f"🚀 start processing {len(pairs)} comparisons...")
    
    for saudi_id, foreign_id in pairs:
        print(f"🔄 processing {saudi_id} with {foreign_id}...")
        try:
            # تنفيذ المقارنة وحفظها تلقائياً في قاعدة البيانات
            result = await comparator.compare_by_ids(saudi_id, foreign_id, db, language="ar")
            
            if "error" in result:
                print(f"⚠️ comparison failed ({saudi_id}, {foreign_id}): {result['error']}")
            else:
                print(f"✅ comparison and save successful ({saudi_id}, {foreign_id})")
                
        except Exception as e:
            print(f"❌ unexpected error ({saudi_id}, {foreign_id}): {str(e)}")
        
        # انتظار بسيط لتجنب حدود الاستخدام (Rate Limits) للذكاء الاصطناعي
        await asyncio.sleep(1)

    db.close()
    print("\n✨ all comparisons completed successfully!")

if __name__ == "__main__":
    asyncio.run(batch_compare())