import json
from typing import Dict, Any, List
from core.llm_service import LLMService

def detect(text: str) -> str:
    """Test compatibility: detect language using the Translator logic."""
    try:
        # Simple language detection based on character sets
        japanese_chars = set('あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもやゆよらりるれろわをんアイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン')
        if any(char in japanese_chars for char in text):
            return 'ja'
        else:
            return 'en'
    except Exception:
        return 'en'

class Translator:
    """Handles translation between English and Japanese for Mercari searches"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def detect_language(self, text: str) -> str:
        """
        Detect the language of the input text
        Returns 'en' for English, 'ja' for Japanese, 'en' as default
        """
        return detect(text)
    
    def translate_to_japanese(self, english_query: str, query_filters: Dict[str, Any] = None) -> str:
        """
        Translate English query to Japanese for effective Mercari searching
        Focus on translating key product terms
        """
        try:
            system_prompt = """You are a translator specializing in e-commerce and product searches.
            Translate the English product search query to Japanese, focusing on terms that would be
            effective for searching on Mercari Japan.
            
            Consider:
            - Product names and categories
            - Brand names (keep in original if commonly used)
            - Colors, sizes, and other attributes
            - Natural Japanese search terms that Japanese users would use
            
            Respond with just the translated Japanese search query."""
            
            response = self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate this product search query to Japanese: {english_query}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            japanese_query = response.choices[0].message.content.strip()
            return japanese_query
            
        except Exception as e:
            # Fallback: use original query
            return english_query
    
    def translate_to_english(self, japanese_query: str) -> str:
        """
        Translate Japanese query to English
        """
        try:
            system_prompt = """You are a translator specializing in e-commerce and product searches.
            Translate the Japanese product search query to English.
            
            Respond with just the translated English search query."""
            
            response = self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Translate this Japanese product search query to English: {japanese_query}"}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            english_query = response.choices[0].message.content.strip()
            return english_query
            
        except Exception as e:
            # Fallback: use original query
            return japanese_query
    
    def translate_query(self, query: str, source_lang: str, target_lang: str, context: Dict[str, Any] = None) -> str:
        """
        Translate query between languages
        """
        if source_lang == target_lang:
            return query
        
        if target_lang == 'ja':
            return self.translate_to_japanese(query, context or {})
        elif target_lang == 'en':
            return self.translate_to_english(query)
        else:
            return query
    
    def translate_product_data(self, product_data: Dict[str, Any], source_lang: str, target_lang: str) -> Dict[str, Any]:
        """
        Translate product data between languages
        """
        if source_lang == target_lang:
            return product_data
        
        translated_data = product_data.copy()
        
        try:
            # Translate name and description
            if target_lang == 'ja':
                if 'name' in translated_data:
                    translated_data['name'] = self.translate_to_japanese(translated_data['name'], {})
                if 'description' in translated_data:
                    translated_data['description'] = self.translate_to_japanese(translated_data['description'], {})
            elif target_lang == 'en':
                if 'name' in translated_data:
                    translated_data['name'] = self.translate_to_english(translated_data['name'])
                if 'description' in translated_data:
                    translated_data['description'] = self.translate_to_english(translated_data['description'])
        except Exception:
            # Return original data if translation fails
            pass
        
        return translated_data
    
    def translate_list(self, items: List[str], source_lang: str, target_lang: str) -> List[str]:
        """
        Translate a list of items between languages
        """
        if source_lang == target_lang:
            return items
        
        translated_items = []
        for item in items:
            try:
                if target_lang == 'ja':
                    translated_items.append(self.translate_to_japanese(item, {}))
                elif target_lang == 'en':
                    translated_items.append(self.translate_to_english(item))
                else:
                    translated_items.append(item)
            except Exception:
                # Keep original item if translation fails
                translated_items.append(item)
        
        return translated_items
    
    def get_japanese_keywords(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate filter keywords to Japanese
        """
        if not filters.get('product_keywords'):
            return filters
        
        translated_filters = filters.copy()
        
        try:
            keywords_text = ", ".join(filters['product_keywords'])
            system_prompt = """Translate these product keywords to Japanese equivalents 
            that would be commonly used on Mercari Japan. Return as comma-separated list."""
            
            response = self.llm_service.client.chat.completions.create(
                model=self.llm_service.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": keywords_text}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            japanese_keywords = [kw.strip() for kw in response.choices[0].message.content.split(',')]
            translated_filters['product_keywords'] = japanese_keywords
            
        except Exception as e:
            # Keep original keywords if translation fails
            pass
        
        return translated_filters
