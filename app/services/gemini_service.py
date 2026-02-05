import google.generativeai as genai
import settings

class geminiService:
    """نقطة التواصل مع Gemini API
    """

    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL_NAME)

        self.generation_config={
            "temperature" : 0.4,
            "top_p" : 0.95,
            "top_k" : 40,
            "max_output_tokens" : 1024
        }
        self.safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
        ]
        
    def generate_answer(self, prompt: str) ->str :
        """ توليد إجابة من Gemini API بناءً على السؤال المقدم

        Args:
            prompt (str): السؤال الذي سيتم طرح

        Returns:
            str: الإجابة التي تم توليدها من Gemini API
        """
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config,
                safety_settings=self.safety_settings
            )
            return response.text.strip() if response.text else None
        except Exception as e:
            print(f"Error generating answer: {e}")  
            return None    

    def generate_with_context(self, question: str, context: str) -> str:
        """ توليد إجابة من Gemini API بناءً على السؤال المقدم و السياق مع RAG 

        Args:
            question (str): السؤال الذي سيتم طرح
            context (str): السياق الذي سيتم استخدامه في توليد الإجابة

        Returns:
            str: الإجابة التي تم توليدها من Gemini API
        """
        try:
            prompt = f"""أنت مساعد قانوني متخصص. أجب بناءً على النصوص القانونية المُقدمة فقط.
                **النصوص القانونية:**
                {context}

                **سؤال المستخدم:**
                {question}

                **تعليمات:**
                - أجب بناءً على النصوص فقط
                - استخدم لغة واضحة وبسيطة
                - اذكر الدولة عند الإجابة
                - لا تختلق معلومات

                الإجابة:"""
            response = self.generate_answer(prompt)
            return response if response else None
        except Exception as e:
            print(f"Error generating answer: {e}")  
            return None    
