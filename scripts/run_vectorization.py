import asyncio
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import LegalContent
from app.core.embeddings import generate_embedding

async def vectorize_all_laws():
    db = SessionLocal()
    print("📡 Fetching laws without embeddings...")
    
    # جلب القوانين التي لم يتم توليد Embedding لها بعد، مع استبعاد المواد غير المرقمة (N/A)
    laws = db.query(LegalContent).filter(
        LegalContent.embedding == None,
        LegalContent.article_number != 'N/A',
        LegalContent.article_number != None,
        LegalContent.article_number != ''
    ).all()
    total = len(laws)
    
    if total == 0:
        print("✅ All laws already have embeddings.")
        return

    print(f"🚀 Starting vectorization for {total} laws...")
    
    for i, law in enumerate(laws):
        try:
            # نستخدم العنوان + النص ليكون الـ Embedding غنياً بالمعلومات
            combined_text = f"{law.title} {law.original_text}"
            vector = generate_embedding(combined_text)
            
            law.embedding = vector
            if (i + 1) % 50 == 0:
                db.commit()
                print(f"✅ Processed {i + 1}/{total} laws...")
                
        except Exception as e:
            print(f"❌ Error in law {law.id}: {e}")
            continue
            
    db.commit()
    print(f"🎉 Successfully vectorized {total} laws!")
    db.close()

if __name__ == "__main__":
    asyncio.run(vectorize_all_laws())