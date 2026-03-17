from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent, SystemConfig
from google.genai import types
from app.utils.helpers import clean_and_parse_json
import json

class LawRanker(GeminiService):
    """Expert for evaluating the importance of legal articles for the public and visitors"""

    def _build_rank_prompt(self, law_title: str, law_text: str, category: str, template: str = None) -> str:
        """بناء البرومبت باستخدام قالب (Template) سواء من قاعدة البيانات أو الافتراضي"""
        
        if not template:
            template = """
            Analyze the importance of this legal article for a typical tourist or resident in the country.
            Provide a score from 1 to 10 and a brief reason in English.

            Article Details:
            - Title: {law_title}
            - Category: {category}
            - Text: {law_text}

            Scoring Criteria:
            - 9-10 (Critical): Rules governing direct public behavior, safety, or laws with severe penalties like high fines, detention, or deportation.
            - 7-8 (High): Common daily rules that most tourists will encounter.
            - 5-6 (Medium): Important procedures or documentation that affect the overall journey.
            - 1-4 (Low): Technical definitions or internal government procedures.

            Respond strictly in JSON format.
            """

        return template.format(
            law_title=law_title,
            law_text=law_text,
            category=category
        )

    async def rank_law(self, db: Session, law_id: int) -> dict:
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law: return {"error": "Law not found"}

        category_name = law.category.name if law.category else "General"
        
        # 1. جلب البرومبت من قاعدة البيانات (SystemConfig) إذا وجد
        db_config = db.query(SystemConfig).filter(SystemConfig.key == "rank_prompt").first()
        template = db_config.value if db_config else None
        
        prompt = self._build_rank_prompt(law.title, law.original_text, category_name, template)

        try:
            # Using response_schema to force structured output and enable response.parsed
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "score": {"type": "INTEGER"},
                        "reason": {"type": "STRING"}
                    },
                    "required": ["score", "reason"]
                },
                temperature=0.2 # Lower temperature for more consistent results
            )

            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            
            result = response.parsed
            
            # Fallback using helper if parsing failed
            if not result and response.text:
                result = clean_and_parse_json(response.text)

            if not result:
                return {"error": "Model returned empty or invalid response"}
                
            score = result.get("score", 0)
            reason = result.get("reason", "")

            # Update database
            law.importance_score = score
            law.importance_reason = reason
            db.commit()

            return {
                "id": law_id,
                "title": law.title,
                "score": score,
                "reason": reason
            }
        except Exception as e:
            db.rollback()
            return {"error": str(e)}