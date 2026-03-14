from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent
from google.genai import types
import asyncio
import json

from app.utils.helpers import clean_and_parse_json

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
        
        result = response.parsed
        if not result and response.text:
            result = clean_and_parse_json(response.text)
            
        return result

    async def simplify(self, law_id: int, db: Session, language: str = "ar") -> dict:
        """
        Main method to simplify legal text and save to DB.
        """
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law:
            return {"error": "Law not found"}
            
        target_lang = "Arabic" if language == "ar" else "English"
        category_name = law.category.name if law.category else "General"
        
        prompt = self._build_prompt(law.title, law.original_text, category_name, target_lang)

        try:
            # Using response_schema to force structured output and enable response.parsed
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "summary": {"type": "STRING"},
                        "punishment": {"type": "STRING"}
                    },
                    "required": ["summary", "punishment"]
                },
            )

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            result_json = response.parsed
            if not result_json and response.text:
                result_json = clean_and_parse_json(response.text)

            if not result_json:
                return {"error": "Failed to generate simplification"}
            
            summary = result_json.get("summary", "")
            punishment = result_json.get("punishment", "")
            
            # تجهيز النص النهائي المدمج
            simplified_output = summary
            if punishment and punishment.lower() not in ["none", "لا يوجد", "n/a", ""]:
                simplified_output = f"{summary}\n\nالعقوبة: {punishment}"

            # 2. حفظ البيانات في DB
            law.simplified_text = simplified_output.strip()
            db.commit()
            
            return {
                "id": law_id,
                "summary": summary,
                "punishment": punishment,
                "full_simplified": simplified_output
            }
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}

    def _build_prompt(self, title: str, law_text: str, category: str, target_lang: str) -> str:
        """بناء البرومبت بلغة طبيعية واضحة لتبسيط النص"""
        return f"""
        Simplify this legal article for a regular person.
        Provide the output in {target_lang}.

        Article Details:
        - Title: {title}
        - Category: {category}
        - Original Text: {law_text}

        Requirements:
        1. Summary: One or two simple and clear sentences summarizing the core rule.
        2. Punishment: Clear explanation of penalties if mentioned, otherwise write 'لا يوجد عقوبات'.

        Constraints:
        - Use friendly, everyday language.
        - Focus on what the person MUST or MUST NOT do.
        - Be extremely concise.
        - Do not change the core meaning of the rule.
        - Do not include any additional information.
        - Do not include any explanations or notes.
        - Respond strictly in JSON format.
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
