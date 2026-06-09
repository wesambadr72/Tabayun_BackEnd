from sqlalchemy.orm import Session
from app.db.models import LegalContent, ComparativeLaw, SystemConfig
from app.services.openai_service import OpenAIService
from app.utils.helpers import clean_and_parse_json


class LawComparator:
    def __init__(self):
        self.ai = OpenAIService()

    async def compare_by_ids(self, saudi_law_id: int, foreign_law_id: int, db: Session, language: str = "ar") -> dict:
        try:
            saudi_law = db.query(LegalContent).filter(LegalContent.id == saudi_law_id).first()
            foreign_law = db.query(LegalContent).filter(LegalContent.id == foreign_law_id).first()

            if not saudi_law or not foreign_law:
                return {"error": "One or both laws not found in database."}

            target_lang = "Arabic" if language == "ar" else "English"

            db_config = db.query(SystemConfig).filter(SystemConfig.key == "comparison_prompt").first()
            template = db_config.value if db_config else None

            prompt = self._build_comparison_prompt(
                saudi_law.title, saudi_law.original_text,
                foreign_law.country, foreign_law.title, foreign_law.original_text,
                target_lang, template,
            )

            raw = await self.ai.generate_answer(prompt)
            result_json = clean_and_parse_json(raw) if raw else None

            if not result_json:
                return {"error": "Failed to generate comparison"}

            summary = result_json.get("comparison_summary", "No summary generated")
            self._save_comparison_to_db(db, saudi_law_id, foreign_law_id, summary)

            return {
                "id": saudi_law_id,
                "foreign_id": foreign_law_id,
                "comparison_text": summary,
                "structured_result": result_json,
            }
        except Exception as e:
            db.rollback()
            return {"error": str(e)}

    def _build_comparison_prompt(self, saudi_title, saudi_text, foreign_country, foreign_title, foreign_text, target_lang, template=None) -> str:
        if not template:
            template = """Compare these two legal articles and provide a brief summary of the differences for a tourist.
The output must be in {target_lang}.

Saudi Law:
- Title: {saudi_title}
- Text: {saudi_text}

Foreign Law ({foreign_country}):
- Title: {foreign_title}
- Text: {foreign_text}

Requirements:
1. comparison_summary: ONE punchy sentence comparing both.
2. saudi_point: Key rule in Saudi Arabia in one short sentence.
3. foreign_point: Key rule in the other country in one short sentence.
4. conclusion: One short practical advice for the traveler in {target_lang}.

Respond strictly in JSON format with keys: comparison_summary, saudi_point, foreign_point, conclusion."""

        return template.format(
            saudi_title=saudi_title, saudi_text=saudi_text,
            foreign_country=foreign_country,
            foreign_title=foreign_title, foreign_text=foreign_text,
            target_lang=target_lang,
        )

    def _save_comparison_to_db(self, db: Session, saudi_id: int, foreign_id: int, summary_text: str):
        try:
            comparison = db.query(ComparativeLaw).filter(
                ComparativeLaw.saudi_law_id == saudi_id,
                ComparativeLaw.foreign_law_id == foreign_id,
            ).first()

            if not comparison:
                comparison = ComparativeLaw(saudi_law_id=saudi_id, foreign_law_id=foreign_id, summary=summary_text)
                db.add(comparison)
            else:
                comparison.summary = summary_text

            db.commit()
        except Exception as e:
            db.rollback()
            raise e
