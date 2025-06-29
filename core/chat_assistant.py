import json
import os
from typing import Dict, List, Any, Optional
from openai import OpenAI

class ChatAssistant:
    """Advanced Chat Assistant that uses LLM function calling for natural language query processing"""
    
    def __init__(self, api_key=None, mock_mode=False):
        self.model = "gpt-4o"
        self.mock_mode = mock_mode or (os.environ.get("LLM_MOCK_MODE") == "1")
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.mock_mode:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
        
        # Define the function schema for query parsing
        self.query_parsing_tools = [
            {
                "type": "function",
                "function": {
                    "name": "parse_shopping_query",
                    "description": "Parse a natural language shopping query to extract search parameters for Mercari Japan",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "keywords": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "Main product keywords to search for"
                            },
                            "japanese_keywords": {
                                "type": "array", 
                                "items": {"type": "string"},
                                "description": "Japanese translations of keywords for Mercari search"
                            },
                            "category": {
                                "type": "string",
                                "description": "Product category (Electronics, Fashion, Home, etc.)",
                                "enum": ["Electronics", "Fashion", "Home", "Sports", "Books", "Toys", "Beauty", "Automotive", "Other"]
                            },
                            "price_preference": {
                                "type": "string",
                                "description": "Price preference from user query",
                                "enum": ["cheap", "budget", "affordable", "mid_range", "premium", "luxury", "any"]
                            },
                            "condition_preference": {
                                "type": "string", 
                                "description": "Preferred condition",
                                "enum": ["new", "like_new", "good", "acceptable", "any"]
                            },
                            "brand": {
                                "type": "string",
                                "description": "Specific brand mentioned"
                            },
                            "color": {
                                "type": "string",
                                "description": "Color preference"
                            },
                            "size": {
                                "type": "string",
                                "description": "Size preference"
                            },
                            "urgency": {
                                "type": "string",
                                "description": "How urgent the search is",
                                "enum": ["immediate", "soon", "casual", "browsing"]
                            },
                            "search_intent": {
                                "type": "string",
                                "description": "User's search intent",
                                "enum": ["buy_now", "research", "compare", "browse"]
                            }
                        },
                        "required": ["keywords", "japanese_keywords"]
                    }
                }
            }
        ]
    
    def parse_natural_language_query(self, query: str, language: str = "en") -> Dict[str, Any]:
        """
        Parse natural language query using LLM function calling
        Returns structured search parameters for Mercari
        """
        if self.mock_mode:
            return {
                "keywords": ["nintendo", "switch"],
                "japanese_keywords": ["ニンテンドー", "スイッチ"],
                "category": "Electronics",
                "price_preference": "any",
                "condition_preference": "any",
                "brand": None,
                "color": None,
                "size": None,
                "urgency": "casual",
                "search_intent": "browse"
            }
        
        system_prompt = """You are an expert shopping assistant for Mercari Japan. 
        Parse user queries to extract search parameters and translate keywords to Japanese.
        
        Guidelines:
        - Extract main product keywords and translate them to Japanese
        - Identify category, price preferences, and condition preferences
        - Detect brand names, colors, and sizes
        - Understand urgency and search intent
        - Be accurate with Japanese translations for better search results
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this shopping query: {query}"}
                ],
                tools=self.query_parsing_tools,
                tool_choice={"type": "function", "function": {"name": "parse_shopping_query"}},
                temperature=0.1
            )
            
            # Extract function call result
            tool_call = response.choices[0].message.tool_calls[0]
            function_args = json.loads(tool_call.function.arguments)
            
            # Ensure required fields
            if not function_args.get("keywords"):
                function_args["keywords"] = [query.lower()]
            if not function_args.get("japanese_keywords"):
                function_args["japanese_keywords"] = [query]
            
            return function_args
            
        except Exception as e:
            print(f"Error parsing query with LLM: {e}")
            # Fallback parsing
            return {
                "keywords": [query.lower()],
                "japanese_keywords": [query],
                "category": "Other",
                "price_preference": "any",
                "condition_preference": "any",
                "brand": None,
                "color": None,
                "size": None,
                "urgency": "casual",
                "search_intent": "browse"
            }
    
    def generate_mercari_search_url(self, parsed_query: Dict[str, Any]) -> str:
        """
        Generate optimized Mercari Japan search URL from parsed query
        """
        base_url = "https://jp.mercari.com/search"
        
        # Use Japanese keywords for better results
        keywords = " ".join(parsed_query.get("japanese_keywords", []))
        
        params = {
            "keyword": keywords,
            "sort": "created_time",
            "order": "desc",
            "status": "on_sale"
        }
        
        # Add category if specified
        category = parsed_query.get("category")
        if category and category != "Other":
            # Map categories to Mercari category IDs
            category_mapping = {
                "Electronics": "electronics",
                "Fashion": "fashion",
                "Home": "home",
                "Sports": "sports",
                "Books": "books",
                "Toys": "toys",
                "Beauty": "beauty",
                "Automotive": "automotive"
            }
            if category in category_mapping:
                params["category"] = category_mapping[category]
        
        # Add price range based on preference
        price_pref = parsed_query.get("price_preference", "any")
        if price_pref == "cheap":
            params["price_min"] = "0"
            params["price_max"] = "5000"
        elif price_pref == "budget":
            params["price_min"] = "0"
            params["price_max"] = "10000"
        elif price_pref == "affordable":
            params["price_min"] = "0"
            params["price_max"] = "20000"
        elif price_pref == "premium":
            params["price_min"] = "50000"
            params["price_max"] = "1000000"
        
        # Add condition filter
        condition = parsed_query.get("condition_preference")
        if condition and condition != "any":
            params["condition"] = condition
        
        # Build URL
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"
    
    def generate_search_reasoning(self, original_query: str, parsed_query: Dict[str, Any], products: List[Dict]) -> str:
        """
        Generate intelligent reasoning for search results
        """
        if self.mock_mode:
            return f"I found {len(products)} products matching your query: '{original_query}'. Here are the best matches based on your preferences."
        
        system_prompt = """You are a helpful shopping assistant. Explain why these products match the user's query.
        Be conversational, mention key features, and explain the reasoning behind your recommendations.
        Keep it concise but informative."""
        
        products_summary = ""
        for i, product in enumerate(products[:3], 1):
            products_summary += f"""
Product {i}: {product.get('name', 'Unknown')}
- Price: ¥{product.get('price', 0):,}
- Condition: {product.get('condition', 'Unknown')}
- Category: {product.get('category', 'Unknown')}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"""
User query: "{original_query}"
Parsed preferences: {json.dumps(parsed_query, indent=2)}
Found products:
{products_summary}

Please explain why these products match the user's needs and preferences.
"""}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error generating reasoning: {e}")
            return f"I found {len(products)} products matching your query: '{original_query}'. Here are the best matches based on your preferences."
    
    def extract_search_filters(self, parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert parsed query to search filters for the scraper
        """
        filters = {}
        
        # Add category
        if parsed_query.get("category") and parsed_query["category"] != "Other":
            filters["category"] = parsed_query["category"]
        
        # Add price range
        price_pref = parsed_query.get("price_preference", "any")
        if price_pref == "cheap":
            filters["price_range"] = {"min": 0, "max": 5000}
        elif price_pref == "budget":
            filters["price_range"] = {"min": 0, "max": 10000}
        elif price_pref == "affordable":
            filters["price_range"] = {"min": 0, "max": 20000}
        elif price_pref == "premium":
            filters["price_range"] = {"min": 50000, "max": 1000000}
        
        # Add condition
        if parsed_query.get("condition_preference") and parsed_query["condition_preference"] != "any":
            filters["condition"] = parsed_query["condition_preference"]
        
        # Add brand
        if parsed_query.get("brand"):
            filters["brand"] = [parsed_query["brand"]]
        
        # Add color
        if parsed_query.get("color"):
            filters["color"] = parsed_query["color"]
        
        # Add size
        if parsed_query.get("size"):
            filters["size"] = parsed_query["size"]
        
        return filters 