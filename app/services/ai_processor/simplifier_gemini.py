from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent
import asyncio

class LawSimplifier(GeminiService):
    """خبير قانوني لتبسيط النصوص القانونية"""
    
    async def simplify(self, law_text: str, language: str = "ar", db: Session = None, law_id: int = None) -> dict:
        """
        Takes a formal legal text and returns it in a simplified format.
        If db and law_id are provided, saves the result to the database.
        """
        target_lang = "Arabic" if language == "ar" else "English"
        
        prompt = f"""
        You are a legal expert and a public awareness content creator. 
        Your task is to transform complex legal texts into a very simple "summary" that anyone can understand.

        Legal Text:
        \"\"\"{law_text}\"\"\"

        Instructions:
        1. Summarize the law in one simple and powerful sentence.
        2. Use clear, everyday language suitable for non-lawyers.
        3. Focus on the main points and avoid jargon.

        Respond ONLY in {target_lang}.
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            # Save to database if db is connected and law_id are provided
            if db and law_id:
                try:
                    law_content = db.query(LegalContent).filter(LegalContent.id == law_id).first()
                    if law_content:
                        law_content.simplified_text = response.text.strip()
                        db.commit()
                        db.refresh(law_content)
                except Exception as e:
                    return {"error": str(e)}
            
            return {
                "simplified_text": response.text.strip()
            }
            
        except Exception as e:
            return {"error": str(e)}
