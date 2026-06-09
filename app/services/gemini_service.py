from google import genai
from app.core.config import settings
import asyncio
import json

class GeminiService:
    """Central service for communicating with Gemini API"""
    
    def __init__(self, api_key: str = None, model_name: str = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model_name = model_name or settings.GEMINI_MODEL_NAME 
        self.client = genai.Client(api_key=self.api_key)
        
        # Default generation settings
        self.config = {
            "temperature": 0.3,
            "top_p": 0.95,
            "top_k": 20,
            "max_output_tokens": 512,
        }

    async def generate_answer(self, prompt: str) -> str:
        """Generate a direct answer from the model"""
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

    async def generate_with_context(
        self,
        question: str,
        context: str,
        language: str = "ar",
        user_name: str | None = None,
        user_country: str | None = None,
    ) -> str:
        """Generate an answer based on context (RAG)"""
        target_lang = "Arabic" if language == "ar" else "English"
        display_name = self._display_name(user_name, language)
        user_country = user_country or "Unknown"
        prompt_payload = {
            "role": "warm, culturally-aware legal guidance assistant",
            "task": "answer_legal_question",
            "audience_profile": {
                "name_to_address": display_name,
                "country_or_culture": user_country,
                "preferred_language": target_lang
            },
            "context": {
                "legal_source": context
            },
            "user_query": question,
            "output_format": {
                "language": target_lang,
                "schema": {
                    "answer": "friendly concise explanation that starts with a brief greeting using name_to_address",
                    "is_legal": "boolean",
                    "has_enough_info": "boolean",
                    "references": "list of articles"
                }
            },
            "tone_guidelines": [
                "Be kind, reassuring, and easy to understand",
                "Address the user by name naturally at the start of the answer",
                "Adapt phrasing and examples to the user's country or culture respectfully",
                "Avoid stereotypes, jokes, or assumptions about the user",
                "Use a helpful conversational style, not a cold legal memo",
                "Keep the answer practical: summary, what it means, and the safest next step",
                "If the user is from Saudi Arabia, use locally familiar polite Arabic phrasing when Arabic is requested",
                "If the user is from another country, mention cultural context only when it helps explain the legal situation"
            ],
            "constraints": [
                "Answer ONLY based on the provided context",
                "Do not invent laws or procedures based on the user's country",
                "If info is missing, set has_enough_info to false",
                "Maintain a professional but warm legal tone",
                "Respond ONLY with the JSON object",
                "If the question is not legal, set is_legal to false",
                "Do not include markdown fences or extra text outside the JSON object"
            ]
        }
        prompt = json.dumps(prompt_payload, ensure_ascii=False)
        try:
            return await self.generate_answer(prompt)
        except Exception as e:
            print(f"Error in GeminiService.generate_with_context: {e}")
            return None 

    def _display_name(self, user_name: str | None, language: str) -> str:
        fallback = "صديقي" if language == "ar" else "friend"
        if not user_name:
            return fallback
        return user_name.strip().split()[0] or fallback
