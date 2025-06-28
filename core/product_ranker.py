from typing import Dict, List, Any
import math

class ProductRanker:
    """Ranks products based on relevance, price, condition, and seller rating"""
    
    def __init__(self):
        # Scoring weights
        self.weights = {
            'relevance': 0.4,
            'price': 0.25,
            'condition': 0.2,
            'seller_rating': 0.15
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
        
        # If category preference, sort by category match first
        if query_filters.get('category'):
            cat = query_filters['category'].lower()
            scored_products.sort(key=lambda x: 0 if x.get('category', '').lower() == cat else 1)
        # If condition preference, sort by condition match first
        if query_filters.get('condition'):
            cond = query_filters['condition'].lower()
            scored_products.sort(key=lambda x: 0 if x.get('condition', '').lower() == cond else 1)
        # If price range, sort by ascending price within range
        if query_filters.get('price_range') and query_filters['price_range'].get('min') is not None and query_filters['price_range'].get('max') is not None:
            minp = query_filters['price_range']['min']
            maxp = query_filters['price_range']['max']
            scored_products.sort(key=lambda x: (0 if minp <= x['price'] <= maxp else 1, x['price']))
        else:
            # Otherwise, sort by score (descending)
            scored_products.sort(key=lambda x: x['_score'], reverse=True)
        
        # Remove duplicates based on name similarity
        unique_products = self._remove_duplicates(scored_products)
        
        return unique_products
    
    def _calculate_score(self, product: Dict, query_filters: Dict[str, Any], all_products: List[Dict]) -> float:
        """Calculate composite score for a product"""
        scores = {}
        
        # Relevance score (based on keyword matching and preferences)
        scores['relevance'] = self._calculate_relevance_score(product, query_filters)
        
        # Price score (considering price range preferences)
        scores['price'] = self._calculate_price_score(product, query_filters, all_products)
        
        # Condition score
        scores['condition'] = self._calculate_condition_score(product, query_filters)
        
        # Seller rating score
        scores['seller_rating'] = self._calculate_seller_rating_score(product)
        
        # Calculate weighted sum
        total_score = sum(scores[criterion] * self.weights[criterion] 
                         for criterion in scores)
        
        return total_score
    
    def _calculate_relevance_score(self, product: Dict, query_filters: Dict[str, Any]) -> float:
        """Calculate relevance score based on keyword matching and preferences"""
        score = 0.0
        
        product_text = f"{product['name']} {product['category']} {product.get('brand', '')}".lower()
        
        # Check query keywords
        if query_filters.get('product_keywords'):
            keywords = [kw.lower() for kw in query_filters['product_keywords']]
            matches = sum(1 for keyword in keywords if keyword in product_text)
            score += matches / len(keywords) if keywords else 0
        
        # Strong bonus for exact brand match
        if query_filters.get('brand') and product.get('brand'):
            if query_filters['brand'].lower() == product['brand'].lower():
                score += 0.5
        
        # Strong bonus for category match
        if query_filters.get('category') and product.get('category'):
            if query_filters['category'].lower() == product['category'].lower():
                score += 0.4
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _calculate_price_score(self, product: Dict, query_filters: Dict[str, Any], all_products: List[Dict]) -> float:
        """Calculate price score considering price range preferences"""
        if not all_products:
            return 0.5
        
        # Check if product is within preferred price range
        price_range = query_filters.get('price_range', {})
        min_pref = price_range.get('min')
        max_pref = price_range.get('max')
        
        product_price = product['price']
        
        # If price range is specified, prioritize products within range
        if min_pref is not None and max_pref is not None:
            if min_pref <= product_price <= max_pref:
                # Within range - give high score, lower price gets higher score
                range_size = max_pref - min_pref
                if range_size > 0:
                    # Normalize within range (lower price = higher score)
                    price_score = 1.0 - ((product_price - min_pref) / range_size)
                    return 0.8 + (price_score * 0.2)  # Base 0.8 + up to 0.2 for price optimization
                else:
                    return 1.0
            else:
                # Outside range - give low score
                return 0.1
        
        # No price range specified - use relative pricing
        prices = [p['price'] for p in all_products]
        min_price = min(prices)
        max_price = max(prices)
        
        if max_price == min_price:
            return 1.0
        
        # Normalize price (lower price gets higher score)
        price_ratio = (max_price - product_price) / (max_price - min_price)
        return price_ratio
    
    def _calculate_condition_score(self, product: Dict, query_filters: Dict[str, Any]) -> float:
        """Calculate condition score with preference consideration"""
        condition = product.get('condition', '').lower()
        base_score = self.condition_scores.get(condition, 0.5)
        
        # Bonus for preferred condition
        preferred_condition = query_filters.get('condition')
        if preferred_condition and condition == preferred_condition.lower():
            return 1.0  # Perfect match gets maximum score
        
        return base_score
    
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
