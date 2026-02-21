from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent, ComparativeLaw
import asyncio

class LawComparator(GeminiService):
    """خبير قانوني للمقارنة بين النصوص القانونية"""
    
    async def compare_by_text(self, law_saudi: str, law_foreign: str, language: str = "ar") -> dict:
        """
        مقارنة قانونين بنصّهما مباشرة.
        """
        target_lang = "Arabic" if language == "ar" else "English"
        
        prompt = f"""
        You are a legal expert specializing in comparative law. 
        Compare the following two legal texts and provide a very brief "Summary Comparison".

        Law in Saudi Arabia:
        \"\"\"{law_saudi}\"\"\"

        Law in Foreign Country:
        \"\"\"{law_foreign}\"\"\"

        Instructions:
        1. Start with a section titled "Summary Comparison".
        2. In "Summary Comparison", provide ONE powerful and concise sentence that captures the main difference between the two laws (similar to a social media awareness post).
        3. Follow it with a very brief bulleted list (max 3 points) explaining the direct impact on a regular person.

        Respond ONLY in {target_lang}.
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            return {
                "comparison_text": response.text,
            }
        except Exception as e:
            return {"error": str(e)}

    async def compare_by_ids(self, db: Session, saudi_law_id: int, foreign_law_id: int, language: str = "ar") -> dict:
        """
        Fetches laws by ID from the database, compares them, and saves the result.
        """
        try:
            # Fetch laws
            saudi_law = db.query(LegalContent).filter(LegalContent.id == saudi_law_id).first()
            foreign_law = db.query(LegalContent).filter(LegalContent.id == foreign_law_id).first()
            
            if not saudi_law or not foreign_law:
                return {"error": "One or both laws not found in database."}
            
            # Generate comparison
            result = await self.compare_by_text(saudi_law.original_text, foreign_law.original_text, language)
            
            if "error" in result:
                return result
                
            summary = result["comparison_text"]
            
            # Save or Update ComparativeLaw
            comparison = db.query(ComparativeLaw).filter(
                ComparativeLaw.saudi_law_id == saudi_law_id,
                ComparativeLaw.foreign_law_id == foreign_law_id
            ).first()
            
            if not comparison:
                comparison = ComparativeLaw(
                    saudi_law_id=saudi_law_id,
                    foreign_law_id=foreign_law_id,
                    summary=summary
                )
                db.add(comparison)
            else:
                comparison.summary = summary
                
            db.commit()
            db.refresh(comparison)
            
            return {
                "comparison_text": summary,
                "comparison_id": comparison.id
            }
            
        except Exception as e:
            return {"error": str(e)}
