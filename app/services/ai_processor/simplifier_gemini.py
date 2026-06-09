from sqlalchemy.orm import Session
from app.db.models import LegalContent, SystemConfig
from app.services.openai_service import OpenAIService
from app.utils.helpers import clean_and_parse_json


class LawSimplifier:
    def __init__(self):
        self.ai = OpenAIService()

    async def simplify(self, law_id: int, db: Session, language: str = "ar") -> dict:
        law = db.query(LegalContent).filter(LegalContent.id == law_id).first()
        if not law:
            return {"error": "Law not found"}

        target_lang = "Arabic" if language == "ar" else "English"
        category_name = law.category.name if law.category else "General"

        db_config = db.query(SystemConfig).filter(SystemConfig.key == "simplification_prompt").first()
        base_prompt = db_config.value if db_config else None
        prompt = self._build_prompt(base_prompt, law.title, law.original_text, category_name, target_lang)

        try:
            raw = await self.ai.generate_answer(prompt)
            result_json = clean_and_parse_json(raw) if raw else None

            if not result_json:
                return {"error": "Failed to generate simplification"}

            summary = result_json.get("summary", "")
            punishment = result_json.get("punishment", "")

            simplified_output = summary
            if punishment and punishment.lower() not in ["none", "لا يوجد", "n/a", ""]:
                simplified_output = f"{summary}\n\nالعقوبة: {punishment}"

            law.simplified_text = simplified_output.strip()
            db.commit()

            return {
                "id": law_id,
                "summary": summary,
                "punishment": punishment,
                "full_simplified": simplified_output,
            }
        except Exception as e:
            db.rollback()
            return {"error": str(e)}

    def _build_prompt(self, base_prompt: str | None, title: str, law_text: str, category: str, target_lang: str) -> str:
        if not base_prompt:
            base_prompt = """Simplify this legal article for a regular person.
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
- Respond strictly in JSON format with keys: summary, punishment."""

        return base_prompt.format(title=title, law_text=law_text, category=category, target_lang=target_lang)
