from sqlalchemy.orm import Session
from app.db.models import LegalContent, SystemConfig
from app.services.openai_service import OpenAIService
from app.utils.helpers import clean_and_parse_json


class LawRanker:
    def __init__(self):
        self.ai = OpenAIService()

    async def rank_law(self, db: Session, law_id: int) -> dict:
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law:
            return {"error": "Law not found"}

        category_name = law.category.name if law.category else "General"

        db_config = db.query(SystemConfig).filter(SystemConfig.key == "rank_prompt").first()
        template = db_config.value if db_config else None
        prompt = self._build_rank_prompt(law.title, law.original_text, category_name, template)

        try:
            raw = await self.ai.generate_answer(prompt)
            result = clean_and_parse_json(raw) if raw else None

            if not result:
                return {"error": "Model returned empty or invalid response"}

            score = result.get("score", 0)
            reason = result.get("reason", "")

            law.importance_score = score
            law.importance_reason = reason
            db.commit()

            return {"id": law_id, "title": law.title, "score": score, "reason": reason}
        except Exception as e:
            db.rollback()
            return {"error": str(e)}

    def _build_rank_prompt(self, law_title: str, law_text: str, category: str, template: str | None = None) -> str:
        if not template:
            template = """Analyze the importance of this legal article for a typical tourist or resident.
Provide a score from 1 to 10 and a brief reason in English.

Article Details:
- Title: {law_title}
- Category: {category}
- Text: {law_text}

Scoring Criteria:
- 9-10 (Critical): Direct public behavior, safety, or severe penalties.
- 7-8 (High): Common daily rules most tourists encounter.
- 5-6 (Medium): Important procedures affecting the journey.
- 1-4 (Low): Technical definitions or internal procedures.

Respond strictly in JSON format with keys: score (integer), reason (string)."""

        return template.format(law_title=law_title, law_text=law_text, category=category)
