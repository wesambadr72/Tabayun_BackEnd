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
        {{
            "role": "professional legal assistant",
            "task": "answer_legal_question",
            "context": {{
                "legal_source": "{context}"
            }},
            "user_query": "{question}",
            "output_format": {{
                "language": "{target_lang}",
                "schema": {{
                    "answer": "concise explanation",
                    "is_legal": "boolean",
                    "has_enough_info": "boolean",
                    "references": "list of articles"
                }}
            }},
            "constraints": [
                "Answer ONLY based on the provided context",
                "If info is missing, set has_enough_info to false",
                "Maintain professional legal tone",
                "Respond ONLY with the JSON object",
                "If the question is not legal, set is_legal to false"
            ]
        }}
        """
        try:
            return await self.generate_answer(prompt)
        except Exception as e:
            print(f"Error in GeminiService.generate_with_context: {e}")
            return None 
