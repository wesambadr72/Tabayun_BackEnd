from google import genai
from app.core.config import settings
import asyncio

class GeminiService:
    """الخدمة المركزية للتواصل مع Gemini API"""
    
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL_NAME 
        self.client = genai.Client(api_key=self.api_key)
        
        # إعدادات التوليد الافتراضية
        self.config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 20,
            "max_output_tokens": 512,
        }

    async def generate_answer(self, prompt: str) -> str:
        """توليد إجابة مباشرة من الموديل"""
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=self.config
            )
            return response.text.strip() if response.text else None
        except Exception as e:
            print(f"Error in GeminiService.generate_answer: {e}")
            return None

    async def generate_with_context(self, question: str, context: str, language: str = "ar") -> str:
        """توليد إجابة بناءً على سياق (RAG)"""
        target_lang = "Arabic" if language == "ar" else "English"
        
        prompt = f"""
        You are a professional legal assistant. Answer the user's question based ONLY on the provided legal context.

        Legal Context:
        \"\"\"{context}\"\"\"

        User Question:
        \"\"\"{question}\"\"\"

        Instructions:
        1. Answer accurately and concisely using the provided context.
        2. If the answer is not in the context, state that you don't have enough information.
        3. Maintain a professional tone.
        4. If the question is not legal, politely decline.

        Respond ONLY in {target_lang}.
        """
        try:
            return await self.generate_answer(prompt)
        except Exception as e:
            print(f"Error in GeminiService.generate_with_context: {e}")
            return None 
