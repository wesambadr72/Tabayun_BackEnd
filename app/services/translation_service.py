import asyncio
from typing import List, Union
from deep_translator import GoogleTranslator
from loguru import logger
import copy

class TranslationService:
    def __init__(self):
        # نستخدم deep-translator لترجمة النصوص
        pass

    async def translate_text(self, text: Union[str, List[str]], target_lang: str = "en") -> Union[str, List[str]]:
        """
        ترجمة نص أو قائمة نصوص باستخدام deep-translator (مجاني ومتوافق).
        """
        if not text:
            return text

        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            
            def do_translate():
                if isinstance(text, list):
                    # ترجمة قائمة من النصوص
                    return translator.translate_batch(text)
                return translator.translate(text)

            result = await asyncio.to_thread(do_translate)
            return result
        except Exception as e:
            logger.error(f"DeepTranslator Error: {str(e)}")
            return text

    async def translate_comparison_list(self, items: List[dict]) -> List[dict]:
        """
        ترجمة قائمة من القوانين/المقارنات (للعناوين والوصف).
        """
        if not items:
            return items

        translated_items = [item.copy() for item in items]
        
        texts_to_translate = []
        for item in translated_items:
            texts_to_translate.append(item.get("title", ""))
            texts_to_translate.append(item.get("description", ""))

        translated = await self.translate_text(texts_to_translate)
        
        if isinstance(translated, list):
            idx = 0
            for item in translated_items:
                item["title"] = translated[idx]
                item["description"] = translated[idx+1]
                idx += 2
        
        return translated_items

    async def translate_comparison_detail(self, detail: dict) -> dict:
        """
        ترجمة تفاصيل المقارنة الكاملة.
        """
        new_detail = copy.deepcopy(detail)
        
        texts_to_translate = [
            new_detail.get("title", ""),
            new_detail.get("saudi_law", {}).get("title", ""),
            new_detail.get("saudi_law", {}).get("text", ""),
            new_detail.get("foreign_law", {}).get("title", ""),
            new_detail.get("foreign_law", {}).get("text", ""),
            new_detail.get("summary", "")
        ]

        translated = await self.translate_text(texts_to_translate)
        
        if isinstance(translated, list):
            new_detail["title"] = translated[0]
            new_detail["saudi_law"]["title"] = translated[1]
            new_detail["saudi_law"]["text"] = translated[2]
            new_detail["foreign_law"]["title"] = translated[3]
            new_detail["foreign_law"]["text"] = translated[4]
            new_detail["summary"] = translated[5]
            
        return new_detail

translation_service = TranslationService()
