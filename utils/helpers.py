import re
from typing import Dict, List

def detect_language(text: str) -> str:
    """
    Simple language detection for English vs Japanese
    Returns 'en' for English, 'ja' for Japanese
    """
    # Count Japanese characters (hiragana, katakana, kanji)
    japanese_chars = len(re.findall(r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', text))
    total_chars = len(re.sub(r'\s', '', text))
    
    if total_chars == 0:
        return 'en'
    
    japanese_ratio = japanese_chars / total_chars
    
    # If more than 30% Japanese characters, consider it Japanese
    return 'ja' if japanese_ratio > 0.3 else 'en'

def format_price(price: int) -> str:
    """Format price with comma separators"""
    return f"¥{price:,}"

def format_product_display(product: Dict) -> str:
    """Format product information for display"""
    return f"""
**{product['name']}**
Price: {format_price(product['price'])}
Condition: {product['condition'].title()}
Seller Rating: {'⭐' * int(product['seller_rating'])} ({product['seller_rating']}/5)
"""

def clean_query(query: str) -> str:
    """Clean and normalize user query"""
    # Remove extra whitespaces
    query = re.sub(r'\s+', ' ', query.strip())
    return query

def extract_price_range(text: str) -> Dict[str, int]:
    """
    Extract price range from text
    Examples: "under 10000", "10000-50000", "less than 20000"
    """
    price_range = {"min": None, "max": None}
    
    # Pattern for ranges like "10000-50000" or "10,000-50,000"
    range_pattern = r'(\d{1,3}(?:,\d{3})*|\d+)\s*[-~]\s*(\d{1,3}(?:,\d{3})*|\d+)'
    range_match = re.search(range_pattern, text)
    
    if range_match:
        min_price = int(range_match.group(1).replace(',', ''))
        max_price = int(range_match.group(2).replace(',', ''))
        price_range["min"] = min_price
        price_range["max"] = max_price
        return price_range
    
    # Pattern for "under X" or "less than X"
    under_pattern = r'(?:under|less than|below)\s*(\d{1,3}(?:,\d{3})*|\d+)'
    under_match = re.search(under_pattern, text.lower())
    
    if under_match:
        max_price = int(under_match.group(1).replace(',', ''))
        price_range["max"] = max_price
        return price_range
    
    # Pattern for "over X" or "more than X"
    over_pattern = r'(?:over|more than|above)\s*(\d{1,3}(?:,\d{3})*|\d+)'
    over_match = re.search(over_pattern, text.lower())
    
    if over_match:
        min_price = int(over_match.group(1).replace(',', ''))
        price_range["min"] = min_price
        return price_range
    
    return price_range

def normalize_condition(condition: str) -> str:
    """
    Normalize condition strings to standard values
    """
    condition = condition.lower().strip()
    
    condition_mapping = {
        'new': 'new',
        'brand new': 'new',
        'unused': 'new',
        'like new': 'like_new',
        'excellent': 'very_good',
        'very good': 'very_good',
        'good': 'good',
        'fair': 'acceptable',
        'acceptable': 'acceptable',
        'poor': 'acceptable'
    }
    
    return condition_mapping.get(condition, condition)
