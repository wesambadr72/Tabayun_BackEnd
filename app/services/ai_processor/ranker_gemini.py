from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent
from google.genai import types
import json

class LawRanker(GeminiService):
    """خبير لتقييم أهمية المواد القانونية للجمهور والزوار"""

    def _build_rank_prompt(self, law_text: str) -> str:
        return f"""
        {{
            "role": "legal_priority_expert",
            "task": "evaluate_law_importance_for_tourists_and_residents",
            "legal_text": "{law_text}",
            "output_format": {{
                "schema": {{
                    "score": "integer from 1 to 10",
                    "reason": "short explanation in Arabic"
                }}
            }},
            "criteria": {{
                "score_10": "Immediate behavioral rules, penalties (fines/jail), or safety prohibitions",
                "score_7_9": "Essential rights, traffic rules, or common public decency rules",
                "score_4_6": "General procedures, documentation requirements, or secondary rules",
                "score_1_3": "Internal government procedures, budget, committee formation, or definitions"
            }},
            "constraints": "Respond ONLY with the JSON object"
        }}
        """

    async def rank_law(self, db: Session, law_id: int) -> dict:
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law: return {"error": "Law not found"}

        prompt = self._build_rank_prompt(law.original_text[:2000]) # نرسل أول 2000 حرف للتوفير

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = response.parsed
            score = result.get("score", 0)
            reason = result.get("reason", "")

            # تحديث قاعدة البيانات
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