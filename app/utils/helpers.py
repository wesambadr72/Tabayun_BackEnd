import json
import re

def clean_and_parse_json(text: str) -> dict:
    """
    Cleans AI-generated text from markdown blocks and extra characters, 
    then parses it into a dictionary.
    """
    if not text:
        return None
        
    try:
        text = text.strip()
        # Remove markdown code blocks if present (```json ... ``` or ``` ... ```)
        if "```" in text:
            # Match content between triple backticks, potentially with a language tag
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
            if match:
                text = match.group(1).strip()
        
        return json.loads(text)
    except Exception as e:
        print(f"Error parsing JSON: {e} | Raw text: {text[:100]}...")
        return None

def get_target_language_code(lang: str = None, user_lang: str = "ar") -> str:
    """
    يتعامل مع مدخلات اللغة من الفرونت إند (مثلاً 'en' أو 'ar')
    ويحولها إلى اسم اللغة الكامل (مثلاً 'English' أو 'Arabic') لاستخدامها في النظام.
    """
    target = lang or user_lang or "ar"
    target = target.lower().strip()
    
    code_to_name = {
        "ar": "Arabic",
        "en": "English",
        "de": "German"
    }
    
    if len(target) == 2:
        return code_to_name.get(target, "Arabic" if target == "ar" else "English")
        
    return target.capitalize()

def get_language_code(lang_name: str) -> str:
    """
    يحول اسم اللغة الكامل إلى رمز ISO (حرفين) لاستخدامه في خدمات الترجمة.
    """
    if not lang_name:
        return "ar"
        
    name_to_code = {
        "arabic": "ar",
        "english": "en",
        "german": "de"
    }
    return name_to_code.get(lang_name.lower(), "en")
        
