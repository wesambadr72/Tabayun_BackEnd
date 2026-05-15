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