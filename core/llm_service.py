import json
import os
import time
from typing import Dict, List, Any
from openai import OpenAI
from core.tag_processor import TagProcessor
import streamlit as st

class LLMService:
    """Service for LLM operations including query parsing and recommendation generation"""
    
    # Simple in-memory rate limiter and cache
    _last_request_time = 0
    _cache = {}
    _cache_ttl = 60  # seconds
    _error_cache_ttl = 30  # seconds for error responses
    # Make rate limit interval configurable via env var (default 20s for low RPM)
    _min_interval = float(os.environ.get("OPENAI_RATE_LIMIT_INTERVAL", 20))
    
    def __init__(self, api_key=None, mock_mode=False):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        self.model = "gpt-4o"
        # Prefer st.secrets for Streamlit Cloud, fallback to env vars
        self.mock_mode = mock_mode or (st.secrets.get("LLM_MOCK_MODE", os.environ.get("LLM_MOCK_MODE")) == "1")
        self.api_key = api_key or st.secrets.get("OPENAI_API_KEY", os.environ.get("OPENAI_API_KEY", "sk-1234abcd5678efgh1234abcd5678efgh1234abcd"))
        if not self.mock_mode:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        self.tag_processor = TagProcessor()
    
    def _rate_limit(self):
        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self._min_interval:
            time.sleep(self._min_interval - elapsed)
        self._last_request_time = time.time()
    
    def _get_cache(self, key):
        entry = self._cache.get(key)
        if entry:
            value, timestamp, is_error = entry
            ttl = self._error_cache_ttl if is_error else self._cache_ttl
            if time.time() - timestamp < ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key, value, is_error=False):
        self._cache[key] = (value, time.time(), is_error)
    
    def parse_query(self, query: str, language: str) -> Dict[str, Any]:
        """
        Parse user query to extract product filters and search parameters
        Uses function calling to structure the output
        """
        cache_key = f"parse_query:{query}:{language}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached
        self._rate_limit()
        result = None
        if self.mock_mode:
            result = {
                "product_keywords": ["iphone"],
                "category": "Electronics",
                "price_range": {"min": 100000, "max": 200000},
                "condition": "new",
                "brand": "Apple",
                "color": None,
                "size": None,
                "features": []
            }
        else:
            system_prompt = """You are a product search query parser for Mercari Japan. 
            Extract relevant information from user queries about products they want to buy.
            
            Extract the following information:
            - product_keywords: List of main product terms
            - category: Product category if identifiable
            - price_range: Dict with min/max if mentioned
            - condition: Preferred condition (new, like_new, good, acceptable)
            - brand: Brand name if mentioned
            - color: Color preference if mentioned
            - size: Size if mentioned
            - features: Any specific features mentioned
            
            Respond with JSON format."""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Parse this query: {query}"}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1
                )
                content = response.choices[0].message.content
                if isinstance(content, str):
                    result = json.loads(content)
                else:
                    result = content
                default_result = {
                    "product_keywords": [],
                    "category": None,
                    "price_range": {"min": None, "max": None},
                    "condition": None,
                    "brand": None,
                    "color": None,
                    "size": None,
                    "features": []
                }
                for key, value in default_result.items():
                    if key not in result:
                        result[key] = value
                self._set_cache(cache_key, result)
                return result
            except Exception as e:
                # Handle 429 Too Many Requests
                if hasattr(e, 'status_code') and e.status_code == 429 or '429' in str(e):
                    result = {
                        "error": "Too many requests to OpenAI API. Please wait a moment and try again.",
                        "product_keywords": [],
                        "category": None,
                        "price_range": {"min": None, "max": None},
                        "condition": None,
                        "brand": None,
                        "color": None,
                        "size": None,
                        "features": []
                    }
                    self._set_cache(cache_key, result, is_error=True)
                    return result
                # Fallback parsing for other errors
                result = {
                    "product_keywords": [query.lower()],
                    "category": None,
                    "price_range": {"min": None, "max": None},
                    "condition": None,
                    "brand": None,
                    "color": None,
                    "size": None,
                    "features": []
                }
                self._set_cache(cache_key, result, is_error=True)
                return result
        self._set_cache(cache_key, result)
        return result
    
    def generate_recommendations(self, original_query: str, products: List[Dict], language: str) -> str:
        """
        Generate recommendation text for the top products using LLM
        Post-process to remove/replace generic 'brand affordable' tags
        """
        if self.mock_mode:
            if not products:
                return "I couldn't find any products matching your criteria. Please try a different search."
            return f"Here are the top {len(products)} products I found for you. Product: {products[0]['name']} is a great match!"
        if not products:
            return "I couldn't find any products matching your criteria. Please try a different search."
        
        language_instruction = "Respond in English" if language == "en" else "Respond in Japanese"
        
        system_prompt = f"""You are a helpful shopping assistant for Mercari Japan. 
        Provide personalized product recommendations based on the user's query and the found products.
        
        {language_instruction}.
        
        For each product, explain why it's a good match for the user's needs.
        Be concise but informative. Mention key features, price value, and condition.
        Format your response in a friendly, conversational tone."""
        
        products_text = ""
        for i, product in enumerate(products, 1):
            products_text += f"""
Product {i}:
- Name: {product['name']}
- Price: ¥{product['price']:,}
- Condition: {product['condition']}
- Seller Rating: {product['seller_rating']}/5
- Category: {product.get('category', 'Unknown')}
"""
        
        user_prompt = f"""
User asked: "{original_query}"

Here are the top products I found:
{products_text}

Please provide recommendations explaining why these products match the user's needs.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            content = response.choices[0].message.content
            # Post-process LLM output to clean up tags/phrasing
            content = self.tag_processor.process_llm_recommendations(content)
            return content if content else f"Here are the top {len(products)} products I found for you. Please check the details below."
        except Exception as e:
            return f"Here are the top {len(products)} products I found for you. Please check the details below."
    
    def call_with_tools(self, messages: List[Dict], tools: List[Dict], tool_choice: str = "auto") -> Dict:
        """
        Make LLM call with tool calling support for agent architecture
        """
        if self.mock_mode:
            return {"content": "Tool call successful", "tool_calls": [], "model": self.model}
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=0.1
            )
            
            # Handle response properly
            message = response.choices[0].message
            content = message.content if message.content else ""
            tool_calls = message.tool_calls if hasattr(message, 'tool_calls') else None
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "model": self.model
            }
            
        except Exception as e:
            print(f"Error in tool calling: {e}")
            return {
                "content": "Error processing request",
                "tool_calls": None,
                "model": self.model
            }
    
    def generate_search_query(self, user_query: str, language: str) -> str:
        """
        Generate optimized search query for Mercari
        """
        try:
            system_prompt = """Generate an optimized search query for Mercari Japan based on the user's request.
            Focus on key product terms, brand names, and attributes that would be effective for searching.
            Keep the query concise but comprehensive."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Generate search query for: {user_query}"}
                ],
                temperature=0.3,
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            return content if content else user_query
            
        except Exception as e:
            return user_query
