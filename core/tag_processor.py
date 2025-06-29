"""
Tag Processor for Mercari Japan Shopping Assistant
Handles intelligent tag generation with pricing logic and removal of generic terms
"""

from typing import Dict, List, Any, Optional
import re

class TagProcessor:
    """Processes and generates intelligent tags for products"""
    
    def __init__(self):
        # Generic terms to remove or replace
        self.generic_terms_to_remove = [
            'brand affordable',
            'affordable brand',
            'cheap brand',
            'budget brand',
            'value brand',
            'economic brand',
            'inexpensive brand',
            'low cost brand',
            'discount brand',
            'budget friendly brand'
        ]
        
        # Price thresholds for affordability tags
        self.price_thresholds = {
            'very_affordable': 2000,  # Under 2000 yen
            'affordable': 5000,       # Under 5000 yen
            'mid_range': 15000,       # Under 15000 yen
            'premium': 50000          # Under 50000 yen
        }
        
        # Product keywords for better categorization
        self.product_keywords = {
            'electronics': ['iphone', 'macbook', 'ipad', 'airpods', 'nintendo', 'switch', 'playstation', 'xbox', 'sony', 'canon', 'nikon'],
            'fashion': ['uniqlo', 'supreme', 'champion', 'louis vuitton', 'chanel', 'fendi', 'rolex'],
            'gaming': ['nintendo', 'switch', 'playstation', 'xbox', 'pokemon', 'duel masters'],
            'collectibles': ['figures', 'cards', 'trading cards', 'pop', 'megahouse']
        }
        
        # Condition mapping for better tags
        self.condition_mapping = {
            'new': 'brand new',
            'like_new': 'like new',
            'very_good': 'excellent condition',
            'good': 'good condition',
            'acceptable': 'fair condition'
        }
    
    def process_product_tags(self, product: Dict, all_products: List[Dict] = None) -> List[str]:
        """
        Process and generate intelligent tags for a product
        
        Args:
            product: Product dictionary
            all_products: List of all products for price comparison (optional)
            
        Returns:
            List of processed tags
        """
        tags = []
        
        # Extract basic tags
        basic_tags = self._extract_basic_tags(product)
        tags.extend(basic_tags)
        
        # Add pricing tags
        pricing_tags = self._generate_pricing_tags(product, all_products)
        tags.extend(pricing_tags)
        
        # Add quality tags
        quality_tags = self._generate_quality_tags(product)
        tags.extend(quality_tags)
        
        # Add category-specific tags
        category_tags = self._generate_category_tags(product)
        tags.extend(category_tags)
        
        # Clean and filter tags
        cleaned_tags = self._clean_tags(tags)
        
        return cleaned_tags
    
    def _extract_basic_tags(self, product: Dict) -> List[str]:
        """Extract basic tags from product data"""
        tags = []
        
        # Add category as tag
        if product.get('category'):
            category = product['category'].lower()
            tags.append(category)
            
            # Add category variations
            if 'electronics' in category:
                tags.append('tech')
            elif 'fashion' in category:
                tags.append('clothing')
            elif 'gaming' in category:
                tags.append('games')
        
        # Add brand as tag (but not generic affordable terms)
        if product.get('brand'):
            brand = product['brand'].lower()
            if not self._is_generic_affordable_term(brand):
                tags.append(brand)
        
        # Extract keywords from name
        if product.get('name'):
            name_words = product['name'].lower().split()
            
            # Add product-specific keywords
            for category, keywords in self.product_keywords.items():
                for keyword in keywords:
                    if keyword in name_words:
                        tags.append(keyword)
            
            # Add size/color if present
            size_patterns = ['xs', 's', 'm', 'l', 'xl', 'xxl', 'small', 'medium', 'large']
            color_patterns = ['black', 'white', 'red', 'blue', 'green', 'yellow', 'pink', 'purple', 'gray', 'brown']
            
            for word in name_words:
                if word in size_patterns:
                    tags.append(f'size {word}')
                elif word in color_patterns:
                    tags.append(word)
        
        return tags
    
    def _generate_pricing_tags(self, product: Dict, all_products: List[Dict] = None) -> List[str]:
        """Generate pricing-related tags"""
        tags = []
        price = product.get('price', 0)
        
        # Determine price category
        if price <= self.price_thresholds['very_affordable']:
            tags.append('very affordable')
            tags.append('budget friendly')
        elif price <= self.price_thresholds['affordable']:
            tags.append('affordable')
            tags.append('good value')
        elif price <= self.price_thresholds['mid_range']:
            tags.append('mid range')
        elif price <= self.price_thresholds['premium']:
            tags.append('premium')
        else:
            tags.append('luxury')
        
        # Compare with other products if available
        if all_products and len(all_products) > 1:
            other_prices = [p.get('price', 0) for p in all_products if p.get('id') != product.get('id')]
            if other_prices:
                avg_price = sum(other_prices) / len(other_prices)
                if price < avg_price * 0.7:  # 30% below average
                    tags.append('great deal')
                elif price < avg_price * 0.9:  # 10% below average
                    tags.append('good deal')
                elif price > avg_price * 1.3:  # 30% above average
                    tags.append('premium price')
        
        return tags
    
    def _generate_quality_tags(self, product: Dict) -> List[str]:
        """Generate quality-related tags"""
        tags = []
        
        # Condition-based tags
        condition = product.get('condition', '').lower()
        if condition in self.condition_mapping:
            tags.append(self.condition_mapping[condition])
        
        # Seller rating tags
        rating = product.get('seller_rating', 0)
        if rating >= 4.8:
            tags.append('top rated seller')
        elif rating >= 4.5:
            tags.append('highly rated')
        elif rating >= 4.0:
            tags.append('well rated')
        
        # Brand quality indicators
        brand = product.get('brand', '').lower()
        premium_brands = ['apple', 'sony', 'nintendo', 'rolex', 'chanel', 'louis vuitton', 'fendi']
        if brand in premium_brands:
            tags.append('premium brand')
        
        return tags
    
    def _generate_category_tags(self, product: Dict) -> List[str]:
        """Generate category-specific tags"""
        tags = []
        category = product.get('category', '').lower()
        name = product.get('name', '').lower()
        
        # Electronics-specific tags
        if 'electronics' in category or any(word in name for word in ['iphone', 'macbook', 'ipad']):
            tags.append('latest tech')
            if 'iphone' in name:
                tags.append('smartphone')
            elif 'macbook' in name:
                tags.append('laptop')
            elif 'ipad' in name:
                tags.append('tablet')
        
        # Gaming-specific tags
        if 'gaming' in category or any(word in name for word in ['nintendo', 'switch', 'playstation', 'xbox']):
            tags.append('gaming')
            if 'switch' in name:
                tags.append('portable gaming')
            elif 'playstation' in name or 'ps5' in name:
                tags.append('console gaming')
        
        # Fashion-specific tags
        if 'fashion' in category:
            tags.append('style')
            if any(word in name for word in ['supreme', 'champion', 'uniqlo']):
                tags.append('streetwear')
            elif any(word in name for word in ['rolex', 'chanel', 'louis vuitton']):
                tags.append('luxury fashion')
        
        # Collectibles-specific tags
        if 'collectibles' in category or any(word in name for word in ['figures', 'cards', 'pokemon']):
            tags.append('collectible')
            if 'pokemon' in name:
                tags.append('pokemon cards')
            elif 'figures' in name:
                tags.append('anime figures')
        
        return tags
    
    def _is_generic_affordable_term(self, text: str) -> bool:
        """Check if text contains generic affordable terms"""
        text_lower = text.lower()
        return any(term in text_lower for term in self.generic_terms_to_remove)
    
    def _clean_tags(self, tags: List[str]) -> List[str]:
        """Clean and filter tags"""
        cleaned = []
        
        for tag in tags:
            # Remove empty tags
            if not tag or tag.strip() == '':
                continue
            
            # Clean the tag
            tag = tag.strip().lower()
            
            # Remove generic affordable terms
            if self._is_generic_affordable_term(tag):
                continue
            
            # Remove very short tags (less than 2 characters)
            if len(tag) < 2:
                continue
            
            # Remove duplicate words
            if tag not in cleaned:
                cleaned.append(tag)
        
        # Limit to reasonable number of tags
        return cleaned[:10]
    
    def process_llm_recommendations(self, recommendation_text: str) -> str:
        """
        Process LLM recommendation text to remove generic affordable terms
        
        Args:
            recommendation_text: Raw recommendation text from LLM
            
        Returns:
            Cleaned recommendation text
        """
        if not recommendation_text:
            return recommendation_text
        
        # Replace generic affordable terms with better alternatives
        processed_text = recommendation_text
        
        # Replace generic affordable terms
        replacements = {
            'brand affordable': 'affordable prices',
            'affordable brand': 'affordable prices',
            'cheap brand': 'affordable prices',
            'budget brand': 'affordable prices',
            'value brand': 'good value',
            'economic brand': 'affordable prices',
            'inexpensive brand': 'affordable prices',
            'low cost brand': 'affordable prices',
            'discount brand': 'discounted price',
            'budget friendly brand': 'budget friendly'
        }
        
        for old_term, new_term in replacements.items():
            processed_text = re.sub(
                re.escape(old_term), 
                new_term, 
                processed_text, 
                flags=re.IGNORECASE
            )
        
        return processed_text
    
    def add_affordable_tag_if_needed(self, product: Dict, all_products: List[Dict] = None) -> List[str]:
        """
        Dynamically add affordable tag if product price is significantly lower than others
        
        Args:
            product: Product to check
            all_products: List of all products for comparison
            
        Returns:
            List of tags to add
        """
        tags_to_add = []
        price = product.get('price', 0)
        
        # Check against price thresholds
        if price <= self.price_thresholds['very_affordable']:
            tags_to_add.append('very affordable')
        
        # Compare with other products
        if all_products and len(all_products) > 1:
            other_prices = [p.get('price', 0) for p in all_products if p.get('id') != product.get('id')]
            if other_prices:
                avg_price = sum(other_prices) / len(other_prices)
                if price < avg_price * 0.7:  # 30% below average
                    tags_to_add.append('great deal')
                elif price < avg_price * 0.9:  # 10% below average
                    tags_to_add.append('affordable prices')
        
        return tags_to_add
    
    def get_tag_summary(self, products: List[Dict]) -> Dict[str, Any]:
        """
        Generate a summary of tags across products
        
        Args:
            products: List of products
            
        Returns:
            Dictionary with tag statistics
        """
        all_tags = []
        price_ranges = []
        
        for product in products:
            tags = self.process_product_tags(product, products)
            all_tags.extend(tags)
            price_ranges.append(product.get('price', 0))
        
        # Count tag frequency
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        # Get price statistics
        if price_ranges:
            avg_price = sum(price_ranges) / len(price_ranges)
            min_price = min(price_ranges)
            max_price = max(price_ranges)
        else:
            avg_price = min_price = max_price = 0
        
        return {
            'total_products': len(products),
            'unique_tags': len(set(all_tags)),
            'most_common_tags': sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5],
            'price_stats': {
                'average': avg_price,
                'min': min_price,
                'max': max_price
            }
        } 