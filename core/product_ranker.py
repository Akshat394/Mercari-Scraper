from typing import Dict, List, Any
import math

class ProductRanker:
    """Ranks products based on relevance, price, condition, and seller rating"""
    
    def __init__(self):
        # Scoring weights
        self.weights = {
            'relevance': 0.3,
            'price': 0.25,
            'condition': 0.25,
            'seller_rating': 0.2
        }
        
        # Condition scoring
        self.condition_scores = {
            'new': 1.0,
            'like_new': 0.9,
            'very_good': 0.8,
            'good': 0.7,
            'acceptable': 0.5
        }
    
    def rank_products(self, products: List[Dict], query_filters: Dict[str, Any]) -> List[Dict]:
        """
        Rank products based on multiple criteria
        Returns sorted list of products with scores
        """
        if not products:
            return []
        
        # Calculate scores for each product
        scored_products = []
        for product in products:
            score = self._calculate_score(product, query_filters, products)
            product_with_score = product.copy()
            product_with_score['_score'] = score
            scored_products.append(product_with_score)
        
        # Sort by score (descending)
        scored_products.sort(key=lambda x: x['_score'], reverse=True)
        
        # Remove duplicates based on name similarity
        unique_products = self._remove_duplicates(scored_products)
        
        return unique_products
    
    def _calculate_score(self, product: Dict, query_filters: Dict[str, Any], all_products: List[Dict]) -> float:
        """Calculate composite score for a product"""
        scores = {}
        
        # Relevance score (based on keyword matching)
        scores['relevance'] = self._calculate_relevance_score(product, query_filters)
        
        # Price score (lower price = higher score, normalized)
        scores['price'] = self._calculate_price_score(product, all_products)
        
        # Condition score
        scores['condition'] = self._calculate_condition_score(product)
        
        # Seller rating score
        scores['seller_rating'] = self._calculate_seller_rating_score(product)
        
        # Calculate weighted sum
        total_score = sum(scores[criterion] * self.weights[criterion] 
                         for criterion in scores)
        
        return total_score
    
    def _calculate_relevance_score(self, product: Dict, query_filters: Dict[str, Any]) -> float:
        """Calculate relevance score based on keyword matching"""
        score = 0.0
        
        product_text = f"{product['name']} {product['category']} {product.get('brand', '')}".lower()
        
        # Check query keywords
        if query_filters.get('product_keywords'):
            keywords = [kw.lower() for kw in query_filters['product_keywords']]
            matches = sum(1 for keyword in keywords if keyword in product_text)
            score += matches / len(keywords) if keywords else 0
        
        # Bonus for exact brand match
        if query_filters.get('brand') and product.get('brand'):
            if query_filters['brand'].lower() == product['brand'].lower():
                score += 0.3
        
        # Bonus for category match
        if query_filters.get('category') and product.get('category'):
            if query_filters['category'].lower() == product['category'].lower():
                score += 0.2
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_price_score(self, product: Dict, all_products: List[Dict]) -> float:
        """Calculate price score (lower price = higher score)"""
        if not all_products:
            return 0.5
        
        prices = [p['price'] for p in all_products]
        min_price = min(prices)
        max_price = max(prices)
        
        if max_price == min_price:
            return 1.0
        
        # Normalize price (lower price gets higher score)
        price_ratio = (max_price - product['price']) / (max_price - min_price)
        return price_ratio
    
    def _calculate_condition_score(self, product: Dict) -> float:
        """Calculate condition score"""
        condition = product.get('condition', '').lower()
        return self.condition_scores.get(condition, 0.5)
    
    def _calculate_seller_rating_score(self, product: Dict) -> float:
        """Calculate seller rating score"""
        rating = product.get('seller_rating', 0)
        return rating / 5.0  # Normalize to 0-1
    
    def _remove_duplicates(self, products: List[Dict]) -> List[Dict]:
        """Remove duplicate products based on name similarity"""
        unique_products = []
        seen_names = set()
        
        for product in products:
            # Simple duplicate detection based on similar names
            name_words = set(product['name'].lower().split())
            
            is_duplicate = False
            for seen_name in seen_names:
                seen_words = set(seen_name.split())
                # If 70% of words overlap, consider it a duplicate
                overlap = len(name_words.intersection(seen_words))
                if overlap / max(len(name_words), len(seen_words)) > 0.7:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_products.append(product)
                seen_names.add(product['name'].lower())
        
        return unique_products
