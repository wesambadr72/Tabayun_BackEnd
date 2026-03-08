from app.services.gemini_service import GeminiService
from sqlalchemy.orm import Session
from app.db.models import LegalContent, ComparativeLaw
import asyncio

class LawComparator(GeminiService):
    """خبير قانوني للمقارنة بين النصوص القانونية"""
    
    async def _get_ai_response(self, prompt: str) -> dict:
        """جلب الاستجابة كـ JSON مباشرة من النموذج"""
        from google.genai import types
        
        response = await self.client.aio.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            )
        )
        return response.parsed

    def _build_comparison_prompt(self, law_saudi: str, law_foreign: str, target_lang: str) -> str:
        """بناء البرومبت للمقارنة بهيكل JSON"""
        return f"""
        {{
            "role": "comparative_law_expert",
            "task": "generate_brief_comparison",
            "saudi_law": "{law_saudi}",
            "foreign_law": "{law_foreign}",
            "output_format": {{
                "language": "{target_lang}",
                "schema": {{
                    "comparison_summary": "ONE powerful and concise sentence capturing the main difference",
                    "saudi_highlight": "One short sentence summarizing the Saudi side",
                    "foreign_highlight": "One short sentence summarizing the foreign side",
                    "key_differences": ["List of 2 max direct impact points"]
                }}
            }},
            "constraints": [
                "Focus on clarity for a regular person",
                "Avoid repeating legal texts",
                "Keep it punchy like a social media awareness post",
                "Respond ONLY with the JSON object"
            ]
        }}
        """

    async def compare_by_text(self, law_saudi: str, law_foreign: str, language: str = "ar") -> dict:
        """
        مقارنة قانونين بنصّهما مباشرة وإخراج النتيجة بهيكل JSON.
        """
        target_lang = "Arabic" if language == "ar" else "English"
        prompt = self._build_comparison_prompt(law_saudi, law_foreign, target_lang)

        try:
            # 1. استخراج الاستجابة كـ JSON جاهز
            result_json = await self._get_ai_response(prompt)
            
            # نستخدم الـ summary كقيمة أساسية للرجوع إليها
            comparison_text = result_json.get("comparison_summary", "No summary generated")

            return {
                "comparison_text": comparison_text,
                "structured_result": result_json
            }
        except Exception as e:
            return {"error": str(e)}

    async def compare_by_ids(self, db: Session, saudi_law_id: int, foreign_law_id: int, language: str = "ar") -> dict:
        """
        Fetches laws by ID from the database, compares them, and saves the result.
        """
        try:
            # Fetch laws
            saudi_law = db.query(LegalContent).filter(LegalContent.id == saudi_law_id).first()
            foreign_law = db.query(LegalContent).filter(LegalContent.id == foreign_law_id).first()
            
            if not saudi_law or not foreign_law:
                return {"error": "One or both laws not found in database."}
            
            # Generate comparison
            result = await self.compare_by_text(saudi_law.original_text, foreign_law.original_text, language)
            
            if "error" in result:
                return result
                
            summary = result["comparison_text"]
            
            # Save or Update ComparativeLaw
            self._save_comparison_to_db(db, saudi_law_id, foreign_law_id, summary)
            
            return {
                "comparison_text": summary,
                "structured_result": result.get("structured_result")
            }
            
        except Exception as e:
            return {"error": str(e)}

    def _save_comparison_to_db(self, db: Session, saudi_id: int, foreign_id: int, summary: str):
        """وظيفة مستقلة للحفظ في قاعدة البيانات"""
        try:
            comparison = db.query(ComparativeLaw).filter(
                ComparativeLaw.saudi_law_id == saudi_id,
                ComparativeLaw.foreign_law_id == foreign_id
            ).first()
            
            if not comparison:
                comparison = ComparativeLaw(
                    saudi_law_id=saudi_id,
                    foreign_law_id=foreign_id, # Error here, fixed below
                    summary=summary
                )
                db.add(comparison)
            else:
                comparison.summary = summary
                
            db.commit()
        except Exception as e:
            db.rollback()
            raise e
