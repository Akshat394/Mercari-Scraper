from typing import Dict, List, Any, Optional
from core.database import DatabaseManager

class DataHandler:
    """Handles data retrieval and processing for Mercari products"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Initialize scraper for real data retrieval
        try:
            from core.mercari_scraper import MercariScraper
            self.scraper = MercariScraper()
            self.use_real_data = True
        except ImportError:
            print("Mercari scraper not available, using database only")
            self.scraper = None
            self.use_real_data = False
    
    def search_products(self, query: str, filters: Dict[str, Any]) -> List[Dict]:
        """
        Search for products based on query and filters
        Uses real Mercari scraping when available, falls back to database
        """
        if not query:
            return []
        
        # Ensure filters is a dictionary
        if not isinstance(filters, dict):
            filters = {}
        
        if self.use_real_data and self.scraper:
            try:
                # Try real Mercari scraping first
                real_products = self.scraper.search_products(query, filters)
                if real_products and len(real_products) > 0:
                    print(f"Found {len(real_products)} real products from Mercari")
                    return real_products
            except Exception as e:
                print(f"Real scraping failed: {e}, falling back to database")
        
        # Fallback to database search
        try:
            db_products = self.db_manager.search_products(query, filters)
            print(f"Database search found {len(db_products)} products")
            return db_products
        except Exception as e:
            print(f"Database search failed: {e}")
            return []
    
    def get_product_details(self, product_id: str) -> Optional[Dict]:
        """Get detailed information for a specific product"""
        if not product_id:
            return None
        
        # Try real scraper first for detailed info
        if self.use_real_data and self.scraper:
            try:
                # Extract URL from product_id if it's a real Mercari product
                if product_id.startswith('mercari_'):
                    # This would need URL reconstruction logic
                    pass
            except Exception as e:
                print(f"Real product details failed: {e}")
        
        try:
            return self.db_manager.get_product_by_id(product_id)
        except Exception as e:
            print(f"Database product details failed: {e}")
            return None
    
    def add_product(self, product_data: Dict) -> bool:
        """Add a new product to the database"""
        if not product_data or not isinstance(product_data, dict):
            return False
        
        try:
            return self.db_manager.add_product(product_data)
        except Exception as e:
            print(f"Error adding product: {e}")
            return False
    
    def get_all_products(self) -> List[Dict]:
        """Get all products from the database"""
        try:
            products = self.db_manager.get_all_products()
            print(f"Retrieved {len(products)} products from database")
            return products
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
    
    def search_mercari_real_time(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Perform real-time search on Mercari Japan
        Returns fresh data from the website
        """
        if not query:
            return []
        
        if not self.use_real_data or not self.scraper:
            print("Real-time search not available, using database")
            return self.search_products(query, filters or {})
        
        try:
            products = self.scraper.search_products(query, filters or {})
            print(f"Real-time search found {len(products)} products")
            return products
        except Exception as e:
            print(f"Real-time search failed: {e}, falling back to database")
            return self.search_products(query, filters or {})
    
    def search_with_ranking(self, query: str, filters: Dict[str, Any] = None) -> List[Dict]:
        """
        Search products and apply ranking
        """
        from core.product_ranker import ProductRanker
        
        # Get products
        products = self.search_products(query, filters or {})
        
        if not products:
            return []
        
        # Apply ranking
        try:
            ranker = ProductRanker()
            ranked_products = ranker.rank_products(products, filters or {})
            print(f"Ranked {len(ranked_products)} products")
            return ranked_products
        except Exception as e:
            print(f"Ranking failed: {e}, returning unranked products")
            return products
    
    def get_products_by_category(self, category: str) -> List[Dict]:
        """Get products by category, using mapped category names for normalization."""
        if not category:
            return []
        
        # Map the category for display purposes
        mapped_category = self.db_manager.map_category(category)
        
        # Search for products with the mapped category
        filters = {"category": mapped_category}
        products = self.search_products("", filters)
        
        # If no products found with exact match, try case-insensitive search
        if not products:
            all_products = self.get_all_products()
            products = [p for p in all_products if p['category'].lower() == mapped_category.lower()]
        
        return products
    
    def get_products_by_brand(self, brand: str) -> List[Dict]:
        """Get products by brand"""
        if not brand:
            return []
        
        filters = {"brand": brand}
        return self.search_products("", filters)
    
    def get_products_by_price_range(self, min_price: int = None, max_price: int = None) -> List[Dict]:
        """Get products by price range"""
        filters = {
            "price_range": {
                "min": min_price,
                "max": max_price
            }
        }
        return self.search_products("", filters)
    
    def close(self):
        """Cleanup resources"""
        if self.scraper:
            try:
                self.scraper.close()
            except Exception as e:
                print(f"Error closing scraper: {e}")
