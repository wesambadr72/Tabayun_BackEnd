import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from sqlalchemy.event import legacy
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
        LegalContent.article_number != "",
        LegalContent.importance_score == 0
    ).all()
    
    total = len(sa_laws)
    print(f"✅ Found {total} valid Saudi legal articles.")
    print("🚀 Starting smart classification... this may take some time.")
    print("-" * 50)

    count = 0
    for law in sa_laws:
        count += 1
        print(f"[{count}/{total}] Evaluating: {law.title[:50]}...")
        
        max_retries = 2
        retry_delay = 15 # Wait longer if model is busy
        
        for attempt in range(max_retries):
            try:
                result = await ranker.rank_law(db, law.id)
                if "error" in result:
                    error_msg = result['error']
                    if "503" in error_msg or "high demand" in error_msg.lower():
                        if attempt < max_retries - 1:
                            print(f"⚠️ Model busy (503). Retrying in {retry_delay}s... (Attempt {attempt + 1}/{max_retries})")
                            await asyncio.sleep(retry_delay)
                            continue
                    print(f"❌ Error in article {law.id}: {error_msg}")
                else:
                    print(f"⭐ Score: {result['score']}/10 | Reason: {result['reason']}")
                break # Success or non-retryable error
            except Exception as e:
                print(f"⚠️ Unexpected failure in article {law.id}: {str(e)}")
                break
        
        # Base delay to respect 5 RPM limit
        await asyncio.sleep(12) 

    print("-" * 50)
    print(f"🎉 Process completed! {count} articles classified successfully.")
    db.close()

if __name__ == "__main__":
    asyncio.run(rank_all_saudi_laws())