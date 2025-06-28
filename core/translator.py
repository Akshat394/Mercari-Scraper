import json
from typing import Dict, Any
from core.llm_service import LLMService

class Translator:
    """Handles translation between English and Japanese for Mercari searches"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def translate_to_japanese(self, english_query: str, query_filters: Dict[str, Any]) -> str:
        """
        Translate English query to Japanese for effective Mercari searching
        Focus on translating key product terms
        """
        system_prompt = """You are a translator specializing in e-commerce and product searches.
        Translate the English product search query to Japanese, focusing on terms that would be
        effective for searching on Mercari Japan.
        
        Consider:
        - Product names and categories
        - Brand names (keep in original if commonly used)
        - Colors, sizes, and other attributes
        - Natural Japanese search terms that Japanese users would use
        
        Respond with just the translated Japanese search query."""
        
        try:
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
        system_prompt = """You are a translator specializing in e-commerce and product searches.
        Translate the Japanese product search query to English.
        
        Respond with just the translated English search query."""
        
        try:
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
