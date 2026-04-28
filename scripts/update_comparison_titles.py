import asyncio
import sys
import os

# حل مشكلة الـ Imports عبر إضافة مسار المشروع الرئيسي يدوياً
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db.models import ComparativeLaw, LegalContent
from app.services.gemini_service import GeminiService

class TitleUpdater(GeminiService):
    async def generate_short_title(self, saudi_text: str, foreign_text: str) -> str:
        prompt = f"""
        Analyze these two legal texts (one from Saudi Arabia and one from another country).
        Identify the core topic they both discuss.
        Provide a very short, professional title in Arabic (2-4 words maximum) that describes the comparison topic.
        Examples: "قانون حزام الأمان", "مخالفات السرعة", "تجديد الرخص".
        Respond ONLY with the title.

        Saudi Text: {saudi_text[:1000]}
        Foreign Text: {foreign_text[:1000]}
        """
        result = await self.generate_answer(prompt)
        return result.strip().replace('"', '') if result else None

async def main():
    db: Session = SessionLocal()
    updater = TitleUpdater()
    
    # التحقق من وجود ID معين في المدخلات
    specific_id = None
    if len(sys.argv) > 1:
        try:
            specific_id = int(sys.argv[1])
        except ValueError:
            print("\nUsage: python scripts/update_comparison_titles.py [comparison_id]")
            print("Example: python scripts/update_comparison_titles.py 10\n")
            return

    try:
        # جلب المقارنات (كلها أو واحدة محددة)
        query = db.query(ComparativeLaw)
        if specific_id:
            query = query.filter(ComparativeLaw.id == specific_id)
            print(f"[+] Target: Comparison ID {specific_id}")
        else:
            print(f"[+] Target: All comparisons")

        comparisons = query.all()
        
        if not comparisons:
            print("[-] No comparisons found matching the criteria.")
            return

        print(f"[+] Found {len(comparisons)} record(s) to process.")

        for comp in comparisons:
            saudi_law = comp.saudi_content
            foreign_law = comp.foreign_content
            
            if not saudi_law or not foreign_law:
                continue

            print(f"[*] Processing Comparison ID: {comp.id}...")
            
            # استنتاج العنوان الجديد عبر AI
            new_title = await updater.generate_short_title(
                saudi_law.original_text, 
                foreign_law.original_text
            )

            if new_title:
                print(f"    - Old Title: {saudi_law.title}")
                print(f"    - New Title: {new_title}")
                
                # تحديث العنوان في جدول legal_contents
                saudi_law.title = new_title
                db.add(saudi_law)
                print(f"    [OK] Updated successfully.")
            else:
                print(f"    [!] Failed to generate title for this comparison.")

        db.commit()
        print("\n[SUCCESS] All titles updated based on comparison topics.")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] An error occurred: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(main())