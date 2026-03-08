from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent
from google.genai import types
import asyncio
import json

class LawSimplifier(GeminiService):
    """خبير قانوني لتبسيط النصوص القانونية"""
    
    async def _get_ai_response(self, prompt: str) -> dict:
        """جلب الاستجابة كـ JSON مباشرة من النموذج"""
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        # النموذج سيرجع قاموس بايثون (dict) مباشرة
        return response.parsed

    async def simplify(self, law_text: str, language: str = "ar", db: Session = None, law_id: int = None) -> dict:
        """
        Main method to simplify legal text and save to DB.
        """
        target_lang = "Arabic" if language == "ar" else "English"
        prompt = self._build_prompt(law_text, target_lang)

        try:
            # 1. استخراج الاستجابة كـ JSON جاهز
            result_json = await self._get_ai_response(prompt)
            
            summary = result_json.get("summary", "")
            punishment = result_json.get("punishment", "")
            
            # تجهيز النص النهائي المدمج
            simplified_output = summary
            if punishment and punishment.lower() not in ["none", "لا يوجد", ""]:
                simplified_output = f"{summary}\n\nالعقوبة: {punishment}"

            # 2. حفظ البيانات في DB
            if db and law_id:
                self._save_to_db(db, law_id, simplified_output)
            
            return {
                "summary": summary,
                "punishment": punishment,
                "full_simplified": simplified_output
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _build_prompt(self, law_text: str, target_lang: str) -> str:
        """بناء البرومبت بهيكل JSON"""
        return f"""
        {{
            "role": "legal_expert",
            "task": "simplify_legal_text",
            "legal_text": "{law_text}",
            "output_format": {{
                "language": "{target_lang}",
                "schema": {{
                    "summary": "One simple and powerful sentence summarizing the core rule of the law",
                    "punishment": "Clear explanation of penalties if explicitly mentioned in this text, else 'None'"
                }}
            }},
            "constraints": [
                "Use clear, everyday language",
                "Focus ONLY on the content of the provided legal text",
                "Be extremely concise",
                "Respond ONLY with the JSON object"
            ]
        }}
        """

    def _save_to_db(self, db: Session, law_id: int, text: str):
        """وظيفة مستقلة للحفظ في قاعدة البيانات"""
        try:
            law_content = db.query(LegalContent).filter(LegalContent.id == law_id).first()
            if law_content:
                law_content.simplified_text = text.strip()
                db.commit()
        except Exception as e:
            db.rollback()
            raise e
