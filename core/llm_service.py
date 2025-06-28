import json
import os
from typing import Dict, List, Any
from openai import OpenAI

class LLMService:
    """Service for LLM operations including query parsing and recommendation generation"""
    
    def __init__(self):
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def parse_query(self, query: str, language: str) -> Dict[str, Any]:
        """
        Parse user query to extract product filters and search parameters
        Uses function calling to structure the output
        """
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
            
            result = json.loads(response.choices[0].message.content)
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
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"Here are the top {len(products)} products I found for you. Please check the details below."
