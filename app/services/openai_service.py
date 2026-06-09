from openai import AsyncOpenAI
from app.core.config import settings
from app.utils.helpers import clean_and_parse_json


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
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful legal assistant that always responds in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=1024,
                temperature=0.3, # Lower temperature for better JSON consistency
                response_format={"type": "json_object"} # Ensure JSON output
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error in OpenAIService.generate_answer: {e}")
            return None

    async def classify_chat_intent(self, question: str, language: str = "ar") -> str | None:
        """Classify a chat message before deciding whether to run RAG."""
        is_arabic = language.lower() in ["ar", "arabic"]
        target_lang = "Arabic" if is_arabic else "English"
        prompt = f"""
You are the intent router for Tabayun, a friendly legal guidance assistant.

Classify the user's message into exactly one intent:

1. "legal"
- The user asks about laws, regulations, rights, duties, penalties, violations, permits, courts, police, immigration, residency, labor, driving, filming, dress rules, public decency, food regulations, tourism rules, or anything that may need legal/regulatory lookup.
- If the message is ambiguous but could reasonably be legal or regulatory, choose "legal" so the database can be searched.

2. "general"
- Greetings, thanks, simple social messages, or questions about Tabayun and what the assistant can do.
- Do not classify a practical external task as general just because it starts with "how", "help", or "can you".

3. "off_topic"
- Requests unrelated to Tabayun's legal/regulatory scope, such as recipes, poems, entertainment, coding help, general homework, personal opinions, or unrelated facts.

User language: {target_lang}
User message:
{question}

Return only this JSON object:
{{
  "intent": "legal"
}}
""".strip()
        raw_response = await self.generate_answer(prompt)
        parsed = clean_and_parse_json(raw_response)
        intent = (parsed or {}).get("intent")
        if intent in {"legal", "general", "off_topic"}:
            return intent
        return None

    async def generate_with_context(
        self,
        question: str,
        context: str,
        language: str = "ar",
        user_name: str | None = None,
        user_country: str | None = None,
    ) -> dict | None:
        """Generate an answer based on retrieved legal context."""
        # Standardize language handling
        is_arabic = language.lower() in ["ar", "arabic"]
        target_lang = "Arabic" if is_arabic else "English"
        
        display_name = self._display_name(user_name, language if is_arabic else "en")
        user_country = user_country or "Unknown"
        
        prompt = f"""
You are Tabayun's warm, confident, culturally-aware legal guidance assistant.
CRITICAL: You MUST provide the "answer" field in {target_lang}.

User profile:
- Name available for occasional use: {display_name}
- Tourist/user country: {user_country}
- Preferred answer language: {target_lang}

User question:
{question}

Legal context from the approved database:
{context}

Answering rules:
- Answer ONLY in {target_lang}.
- Answer only from the legal context above.
- If the context includes "Text fetched from the same source URL", treat it as the freshest reference and compare it with the stored legal text.
- If the context includes "Tourist country comparison context", compare the Saudi rule with the tourist's country rule in 1-2 short sentences.
- Do not compare with the tourist's country if no tourist-country comparison context is provided.
- If the context contains a direct legal rule that answers the question, answer it and set has_enough_info to true.
- If details such as penalty amounts, exceptions, or procedures are missing, do not say "غير متوفر في النص", "غير متاح في السياق", "النص المرفق", or similar wording that exposes system limitations.
- When details are missing, give the available rule confidently, then add a natural next step such as "وللتفاصيل الدقيقة مثل الغرامة أو الإجراء، الأفضل مراجعة الجهة الرسمية المختصة أو الرابط الرسمي." (or equivalent in English if target language is English).
- Never say or imply that Tabayun has weak sources, incomplete data, or insufficient context when a direct rule is available.
- Avoid phrases like "غير متاح هنا", "غير متوفر لدي", "لا أستطيع", "النص المعروض", and "السياق المرفق" (and English equivalents) when answering a direct legal rule.
- Set has_enough_info to false only when the legal context does not answer the user's question at all.
- Do not invent laws, penalty amounts, official procedures, or exceptions.
- Avoid a repeated canned opener.
- Use a confident, friendly, energetic tone. The user should feel helped.
- Start with a varied welcoming phrase when appropriate, then answer the question directly.
- Use a softer style than a legal warning.
- Keep the answer compact and natural: main rule, comparison if available, safest next step.
- Return only a valid JSON object with exactly these keys:
{{
  "answer": "concise explanation in {target_lang}",
  "is_legal": true,
  "has_enough_info": true,
  "references": ["list of article/source names from the legal context"]
}}
""".strip()
        raw_response = await self.generate_answer(prompt)
        return clean_and_parse_json(raw_response)

    def _display_name(self, user_name: str | None, language: str) -> str:
        is_arabic = language.lower() in ["ar", "arabic"]
        fallback = "صديقي" if is_arabic else "friend"
        if not user_name:
            return fallback
        return user_name.strip().split()[0] or fallback
