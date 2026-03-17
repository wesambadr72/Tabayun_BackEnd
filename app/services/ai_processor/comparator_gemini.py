from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent, ComparativeLaw, SystemConfig
import asyncio
from app.utils.helpers import clean_and_parse_json

class LawComparator(GeminiService):
    """خبير قانوني للمقارنة بين النصوص القانونية"""
    
    def _build_comparison_prompt(self, saudi_title: str, saudi_text: str, foreign_country: str, foreign_title: str, foreign_text: str, target_lang: str, template: str = None) -> str:
        """بناء البرومبت باستخدام قالب (Template) سواء من قاعدة البيانات أو الافتراضي"""
        
        if not template:
            template = """
            Compare these two legal articles and provide a brief summary of the differences for a tourist.
            The output must be in {target_lang}.

            Saudi Law:
            - Title: {saudi_title}
            - Text: {saudi_text}

            Foreign Law ({foreign_country}):
            - Title: {foreign_title}
            - Text: {foreign_text}

            Requirements:
            1. Comparison Summary: ONE punchy and clear sentence in {target_lang} comparing both (e.g. 'Both require X, but UK has Y').
            2. Saudi Point: Key rule in Saudi Arabia in one short sentence.
            3. Foreign Point: Key rule in the other country in one short sentence.
            4. Conclusion: One short practical advice for the traveler in {target_lang}.

        Constraints:
        - Focus on the most important difference for a tourist.
        - Keep it very brief and direct.
        - Do not include any additional information.
        - Do not include any explanations or notes.
        - Respond strictly in JSON format.
        """

        return template.format(
            saudi_title=saudi_title,
            saudi_text=saudi_text,
            foreign_country=foreign_country,
            foreign_title=foreign_title,
            foreign_text=foreign_text,
            target_lang=target_lang
        )

    async def compare_by_ids(self, saudi_law_id: int, foreign_law_id: int, db: Session, language: str = "ar") -> dict:
        """
        Fetches laws by ID from the database, compares them, and saves the result.
        """
        try:
            from google.genai import types
            # Fetch laws
            saudi_law = db.query(LegalContent).filter(LegalContent.id == saudi_law_id).first()
            foreign_law = db.query(LegalContent).filter(LegalContent.id == foreign_law_id).first()
            
            if not saudi_law or not foreign_law:
                return {"error": "One or both laws not found in database."}
            
            target_lang = "Arabic" if language == "ar" else "English"
            
            # 1. جلب البرومبت من قاعدة البيانات (SystemConfig) إذا وجد
            db_config = db.query(SystemConfig).filter(SystemConfig.key == "comparison_prompt").first()
            template = db_config.value if db_config else None
            
            prompt = self._build_comparison_prompt(
                saudi_law.title, saudi_law.original_text, 
                foreign_law.country, foreign_law.title, foreign_law.original_text, 
                target_lang, template
            )

            # Using response_schema to force structured output
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "comparison_summary": {"type": "STRING"},
                        "saudi_point": {"type": "STRING"},
                        "foreign_point": {"type": "STRING"},
                        "conclusion": {"type": "STRING"}
                    },
                    "required": ["comparison_summary", "saudi_point", "foreign_point", "conclusion"]
                },
                temperature=0.2
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
                return {"error": "Failed to generate comparison"}
                
            summary = result_json.get("comparison_summary", "No summary generated")
            
            # Save or update comparison in DB using the consolidated method
            self._save_comparison_to_db(db, saudi_law_id, foreign_law_id, summary)
            
            return {
                "id": saudi_law_id,
                "foreign_id": foreign_law_id,
                "comparison_text": summary,
                "structured_result": result_json
            }
            
        except Exception as e:
            db.rollback()
            return {"error": str(e)}

    def _save_comparison_to_db(self, db: Session, saudi_id: int, foreign_id: int, summary_text: str):
        """وظيفة مركزية للحفظ أو التحديث في قاعدة البيانات"""
        try:
            comparison = db.query(ComparativeLaw).filter(
                ComparativeLaw.saudi_law_id == saudi_id,
                ComparativeLaw.foreign_law_id == foreign_id
            ).first()
            
            if not comparison:
                comparison = ComparativeLaw(
                    saudi_law_id=saudi_id,
                    foreign_law_id=foreign_id,
                    summary=summary_text
                )
                db.add(comparison)
            else:
                comparison.summary = summary_text
                
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
