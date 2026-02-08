from app.services.gemini_service import GeminiService
import asyncio

class LawSimplifier(GeminiService):
    """خبير قانوني لتبسيط النصوص القانونية"""
    
    async def simplify(self, law_text: str, language: str = "ar") -> dict:
        """
        Takes a formal legal text and returns it in a simplified format.
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


        Respond ONLY in {target_lang}.
        """

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
            )
            
            return {
                "simplified_text": response.text,
            }
        except Exception as e:
            return {"error": str(e)}
