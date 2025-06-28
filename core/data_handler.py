import json
import re
from typing import Dict, List, Any
from core.sample_data import SAMPLE_MERCARI_DATA

class DataHandler:
    """Handles data retrieval and processing for Mercari products"""
    
    def __init__(self):
        self.sample_data = SAMPLE_MERCARI_DATA
    
    def search_products(self, query: str, filters: Dict[str, Any]) -> List[Dict]:
        """
        Search for products based on query and filters
        In production, this would scrape Mercari Japan
        For now, we use sample data with realistic filtering
        """
        results = []
        
        # Extract search terms
        search_terms = self._extract_search_terms(query, filters)
        
        # Filter sample data based on search criteria
        for product in self.sample_data:
            if self._matches_criteria(product, search_terms, filters):
                results.append(product)
        
        return results
    
    def _extract_search_terms(self, query: str, filters: Dict[str, Any]) -> List[str]:
        """Extract search terms from query and filters"""
        terms = []
        
        # From query
        query_words = re.findall(r'\w+', query.lower())
        terms.extend(query_words)
        
        # From filters
        if filters.get('product_keywords'):
            terms.extend([kw.lower() for kw in filters['product_keywords']])
        
        if filters.get('brand'):
            terms.append(filters['brand'].lower())
        
        if filters.get('category'):
            terms.append(filters['category'].lower())
        
        return list(set(terms))  # Remove duplicates
    
    def _matches_criteria(self, product: Dict, search_terms: List[str], filters: Dict[str, Any]) -> bool:
        """Check if product matches search criteria"""
        # Text matching
        product_text = f"{product['name']} {product['category']} {product.get('brand', '')}".lower()
        
        # Check if any search terms match
        text_match = any(term in product_text for term in search_terms) if search_terms else True
        
        # Price range filter
        price_match = True
        if filters.get('price_range'):
            price_range = filters['price_range']
            if price_range.get('min') and product['price'] < price_range['min']:
                price_match = False
            if price_range.get('max') and product['price'] > price_range['max']:
                price_match = False
        
        # Condition filter
        condition_match = True
        if filters.get('condition'):
            condition_match = product['condition'].lower() == filters['condition'].lower()
        
        # Brand filter
        brand_match = True
        if filters.get('brand'):
            brand_match = product.get('brand', '').lower() == filters['brand'].lower()
        
        return text_match and price_match and condition_match and brand_match
    
    def get_product_details(self, product_id: str) -> Dict:
        """Get detailed information for a specific product"""
        for product in self.sample_data:
            if product['id'] == product_id:
                return product
        return None
