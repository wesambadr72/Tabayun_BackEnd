from app.services.gemini_service import GeminiService
import asyncio

class LawComparator(GeminiService):
    """خبير قانوني للمقارنة بين النصوص القانونية"""
    
    async def compare_by_text(self, law_a: str, law_b: str, language: str = "ar") -> dict:
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

    async def compare_by_ids(self, law_id_a: int, law_id_b: int, language: str = "ar") -> dict:
        """
        مستقبلاً: جلب النصوص من قاعدة البيانات بناءً على المعرفات ثم مقارنتها.
        """
        raise NotImplementedError("Feature to fetch laws by ID is pending database integration.")
