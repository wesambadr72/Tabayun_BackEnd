import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import LegalContent
from app.services.ai_processor.ranker_gemini import LawRanker


async def rank_all_saudi_laws():
    db = SessionLocal()
    ranker = LawRanker()
    
    print("📡 Fetching Saudi laws from database...")
    sa_laws = db.query(LegalContent).filter(
        LegalContent.country == "sa",
        LegalContent.article_number != "N/A",
        LegalContent.article_number != None,
        LegalContent.article_number != ""
    ).all()
    
    total = len(sa_laws)
    print(f"✅ Found {total} valid Saudi legal articles.")
    print("🚀 Starting smart classification... this may take some time.")
    print("-" * 50)

    count = 0
    for law in sa_laws:
        count += 1
        print(f"[{count}/{total}] Evaluating: {law.title[:50]}...")
        
        try:
            result = await ranker.rank_law(db, law.id)
            if "error" in result:
                print(f"❌ Error in article {law.id}: {result['error']}")
            else:
                print(f"⭐ Score: {result['score']}/10 | Reason: {result['reason']}")
        except Exception as e:
            print(f"⚠️ Unexpected failure in article {law.id}: {str(e)}")
        
        # Increased delay to 12 seconds to respect 5 RPM limit (60s / 5 = 12s)
        await asyncio.sleep(12) 

    print("-" * 50)
    print(f"🎉 Process completed! {count} articles classified successfully.")
    db.close()

if __name__ == "__main__":
    asyncio.run(rank_all_saudi_laws())