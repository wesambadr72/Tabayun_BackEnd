import asyncio
from typing import List, Union
from deep_translator import GoogleTranslator
from loguru import logger
import copy

class TranslationService:
    def __init__(self):
        # In-memory cache for translations: {(text, target_lang): translated_text}
        self._cache = {}

    async def translate_text(self, text: Union[str, List[str]], target_lang: str = "en") -> Union[str, List[str]]:
        """
        ترجمة نص أو قائمة نصوص باستخدام deep-translator مع دعم للتخزين المؤقت (Caching).
        """
        if not text:
            return text

        # Handle list input
        if isinstance(text, list):
            results = []
            uncached_indices = []
            uncached_texts = []

            for i, t in enumerate(text):
                cache_key = (t, target_lang)
                if cache_key in self._cache:
                    results.append(self._cache[cache_key])
                else:
                    results.append(None) # Placeholder
                    uncached_indices.append(i)
                    uncached_texts.append(t)

            if uncached_texts:
                try:
                    translator = GoogleTranslator(source='auto', target=target_lang)
                    translated_batch = await asyncio.to_thread(translator.translate_batch, uncached_texts)
                    
                    for i, translated_val in enumerate(translated_batch):
                        idx = uncached_indices[i]
                        original_text = uncached_texts[i]
                        results[idx] = translated_val
                        # Update cache
                        self._cache[(original_text, target_lang)] = translated_val
                except Exception as e:
                    logger.error(f"DeepTranslator Batch Error: {str(e)}")
                    # Fallback to original text for failed translations
                    for i, idx in enumerate(uncached_indices):
                        results[idx] = uncached_texts[i]
            
            return results

        # Handle single string input
        cache_key = (text, target_lang)
        if cache_key in self._cache:
            return self._cache[cache_key]

        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            result = await asyncio.to_thread(translator.translate, text)
            self._cache[cache_key] = result
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
