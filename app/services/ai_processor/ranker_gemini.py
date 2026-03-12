from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent
from google.genai import types
import json

class LawRanker(GeminiService):
    """Expert for evaluating the importance of legal articles for the public and visitors"""

    def _build_rank_prompt(self, law_text: str) -> str:
        return f"""
        {{
            "role": "legal_priority_expert",
            "task": "evaluate_law_importance_for_tourists_and_residents",
            "legal_text": "{law_text}",
            "output_format": {{
                "schema": {{
                    "score": "integer from 1 to 10",
                    "reason": "short explanation in English"
                }}
            }},
            "criteria": {{
                "score_9_10": "Direct behavior in public or safety rules with clear fines, detention, or deportation risk for tourists",
                "score_7_8": "High-frequency daily rules (public decency, dress, photography, basic traffic) that most tourists will face",
                "score_5_6": "Important rights, documentation, and general procedures that affect the tourist journey but not every moment",
                "score_1_4": "Internal government procedures, institutional/budget articles, or technical definitions with minimal direct impact on tourists"
            }},
            "constraints": "Respond ONLY with the JSON object"
        }}
        """

    async def rank_law(self, db: Session, law_id: int) -> dict:
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law: return {"error": "Law not found"}

        prompt = self._build_rank_prompt(law.original_text[:2000]) # Send first 2000 chars to save tokens

        try:
            response = await self.client.aio.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            result = response.parsed
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