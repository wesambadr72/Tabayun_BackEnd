from openai import AsyncOpenAI

from app.core.config import settings


class OpenAIService:
    """Central service for communicating with the OpenAI Responses API."""

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str | None = None,
        reasoning_effort: str = "low",
    ):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model_name = model_name or settings.OPENAI_MODEL_NAME
        self.reasoning_effort = reasoning_effort
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_answer(self, prompt: str) -> str | None:
        """Generate a direct answer from OpenAI."""
        try:
            response = await self.client.responses.create(
                model=self.model_name,
                input=prompt,
                reasoning={"effort": self.reasoning_effort},
                max_output_tokens=1024,
            )
            return response.output_text.strip() if response.output_text else None
        except Exception as e:
            print(f"Error in OpenAIService.generate_answer: {e}")
            return None

    async def generate_with_context(
        self,
        question: str,
        context: str,
        language: str = "ar",
        user_name: str | None = None,
        user_country: str | None = None,
    ) -> str | None:
        """Generate an answer based on retrieved legal context."""
        target_lang = "Arabic" if language == "ar" else "English"
        display_name = self._display_name(user_name, language)
        user_country = user_country or "Unknown"
        prompt = f"""
You are Tabayun's warm, confident, culturally-aware legal guidance assistant.

User profile:
- Name available for occasional use: {display_name}
- Tourist/user country: {user_country}
- Preferred answer language: {target_lang}

User question:
{question}

Legal context from the approved database:
{context}

Answering rules:
- Answer only from the legal context above.
- If the context includes "Text fetched from the same source URL", treat it as the freshest reference and compare it with the stored legal text.
- If the context includes "Tourist country comparison context", compare the Saudi rule with the tourist's country rule in 1-2 short sentences.
- Do not compare with the tourist's country if no tourist-country comparison context is provided.
- If the context contains a direct legal rule that answers the question, answer it and set has_enough_info to true.
- If details such as penalty amounts, exceptions, or procedures are missing, do not say "غير متوفر في النص", "غير متاح في السياق", "النص المرفق", or similar wording that exposes system limitations.
- When details are missing, give the available rule confidently, then add a natural next step such as "وللتفاصيل الدقيقة مثل الغرامة أو الإجراء، الأفضل مراجعة الجهة الرسمية المختصة أو الرابط الرسمي." Do not make the product sound weak.
- Never say or imply that Tabayun has weak sources, incomplete data, or insufficient context when a direct rule is available.
- Avoid phrases like "غير متاح هنا", "غير متوفر لدي", "لا أستطيع", "النص المعروض", and "السياق المرفق" when answering a direct legal rule.
- Set has_enough_info to false only when the legal context does not answer the user's question at all.
- Do not invent laws, penalty amounts, official procedures, or exceptions.
- Avoid a repeated canned opener. Do not start every answer with "أهلًا سلطان، أفهم عليك" or "مرحبًا سلطان".
- Also avoid starting every answer with "أكيد". Vary openings naturally, and sometimes start directly with the answer.
- Use the user's name only when it sounds natural; do not force it into every answer.
- Use a confident, friendly, energetic tone. The user should feel helped, not warned or dismissed.
- Start with a varied welcoming phrase when appropriate, then answer the question directly.
- Prefer natural phrasing like "أكيد، خليني أوضح لك..." or "تمام، القاعدة هنا واضحة..." or "باختصار..." when it fits the question.
- Use a softer style than a legal warning. Prefer calm phrasing like "الأفضل تتجنب..." or "حسب النظام، هذا التصرف يدخل ضمن..." instead of blunt scolding.
- Keep the answer compact and natural: main rule, comparison if available, safest next step.
- Do not overuse cautious disclaimers. Avoid ending every answer with limitations.
- Do not repeat the same next-step sentence across answers. Add a next step only when it is genuinely useful, and vary the wording.
- Avoid stereotypes, jokes, and emojis.
- If the question is not legal, set is_legal to false.

Return only a valid JSON object with exactly these keys:
{{
  "answer": "friendly concise explanation",
  "is_legal": true,
  "has_enough_info": true,
  "references": ["list of article/source names from the legal context"]
}}
""".strip()
        return await self.generate_answer(prompt)

    def _display_name(self, user_name: str | None, language: str) -> str:
        fallback = "صديقي" if language == "ar" else "friend"
        if not user_name:
            return fallback
        return user_name.strip().split()[0] or fallback
