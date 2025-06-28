import json
import os
from typing import Dict, List, Any
from openai import OpenAI

class LLMService:
    """Service for LLM operations including query parsing and recommendation generation"""
    
    def __init__(self, api_key=None, mock_mode=False):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        self.model = "gpt-4o"
        self.mock_mode = mock_mode or (os.environ.get("LLM_MOCK_MODE") == "1")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "sk-1234abcd5678efgh1234abcd5678efgh1234abcd")
        if not self.mock_mode:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
    
    def parse_query(self, query: str, language: str) -> Dict[str, Any]:
        """
        Parse user query to extract product filters and search parameters
        Uses function calling to structure the output
        """
        if self.mock_mode:
            # Return a mock parse result for tests
            return {
                "product_keywords": ["iphone"],
                "category": "Electronics",
                "price_range": {"min": 100000, "max": 200000},
                "condition": "new",
                "brand": "Apple",
                "color": None,
                "size": None,
                "features": []
            }
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
            
            # Handle response format properly
            content = response.choices[0].message.content
            if isinstance(content, str):
                result = json.loads(content)
            else:
                result = content
            
            # Ensure all required fields are present
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
            
            # Merge with defaults
            for key, value in default_result.items():
                if key not in result:
                    result[key] = value
            
            return result
            
        except Exception as e:
            # Fallback parsing
            return {
                "product_keywords": [query.lower()],
                "category": None,
                "price_range": {"min": None, "max": None},
                "condition": None,
                "brand": None,
                "color": None,
                "size": None,
                "features": []
            }
    
    def generate_recommendations(self, original_query: str, products: List[Dict], language: str) -> str:
        """
        Generate recommendation text for the top products using LLM
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
