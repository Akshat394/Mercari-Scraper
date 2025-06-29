from typing import Dict, List, Any, Optional
from core.database import DatabaseManager
import uuid
import time

class DataHandler:
    """Handles data retrieval and processing for Mercari products with search history"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
        # Initialize scraper for real data retrieval
        try:
            from core.mercari_scraper import MercariScraper
            # Enable Selenium for better scraping of dynamic content
            self.scraper = MercariScraper(use_selenium=True)
            self.use_real_data = True
        except ImportError:
            print("Mercari scraper not available, using database only")
            self.scraper = None
            self.use_real_data = False
        
        # Add caching to prevent excessive database queries
        self._cache = {}
        self._cache_timeout = 30  # Cache for 30 seconds
        self._last_cache_cleanup = time.time()
    
    def _get_cache_key(self, method: str, *args) -> str:
        """Generate a cache key for a method call"""
        return f"{method}:{hash(str(args))}"
    
    def _get_from_cache(self, cache_key: str):
        """Get value from cache if not expired"""
        if cache_key in self._cache:
            timestamp, value = self._cache[cache_key]
            if time.time() - timestamp < self._cache_timeout:
                return value
            else:
                del self._cache[cache_key]
        return None
    
    def _set_cache(self, cache_key: str, value):
        """Set value in cache with timestamp"""
        self._cache[cache_key] = (time.time(), value)
        
        # Clean up old cache entries periodically
        if time.time() - self._last_cache_cleanup > 60:  # Clean up every minute
            self._cleanup_cache()
    
    def _cleanup_cache(self):
        """Remove expired cache entries"""
        current_time = time.time()
        expired_keys = [
            key for key, (timestamp, _) in self._cache.items()
            if current_time - timestamp > self._cache_timeout
        ]
        for key in expired_keys:
            del self._cache[key]
        self._last_cache_cleanup = current_time
    
    def search_products(self, query: str, filters: Dict[str, Any], session_id: str = None) -> List[Dict]:
        """
        Search for products based on query and filters
        Uses real Mercari scraping when available, falls back to database
        Stores results in search history for future recommendations
        """
        if not query:
            return []
        
        # Ensure filters is a dictionary
        if not isinstance(filters, dict):
            filters = {}
        
        # Generate session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
        
        products = []
        
        if self.use_real_data and self.scraper:
            try:
                # Try real Mercari scraping first
                real_products = self.scraper.search_products(query, filters)
                if real_products and len(real_products) > 0:
                    print(f"Found {len(real_products)} real products from Mercari")
                    products = real_products
            except Exception as e:
                print(f"Real scraping failed: {e}, falling back to database")
        
        # Fallback to database search if no real products found
        if not products:
            try:
                db_products = self.db_manager.search_products(query, filters)
                print(f"Database search found {len(db_products)} products")
                products = db_products
            except Exception as e:
                print(f"Database search failed: {e}")
                return []
        
        # Store search results in history for future recommendations
        if products:
            try:
                self.db_manager.store_search_results(query, products, session_id)
                print(f"Stored {len(products)} search results in history")
            except Exception as e:
                print(f"Failed to store search history: {e}")
        
        return products
    
    def search_with_history_fallback(self, query: str, filters: Dict[str, Any] = None, session_id: str = None) -> List[Dict]:
        """
        Search for products with fallback to recent search history
        This allows the agent to recommend products from past searches
        """
        if not query:
            return []
        
        # Try current search first
        current_products = self.search_products(query, filters or {}, session_id)
        
        if current_products:
            return current_products
        
        # If no current results, try to get recent products for similar queries
        try:
            recent_products = self.db_manager.get_recent_products_for_query(query, limit=10)
            if recent_products:
                print(f"Found {len(recent_products)} recent products for similar query: {query}")
                return recent_products
        except Exception as e:
            print(f"Failed to get recent products: {e}")
        
        return []
    
    def get_search_history(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        """
        Get search history for display in sidebar
        """
        try:
            return self.db_manager.get_search_history(session_id, limit)
        except Exception as e:
            print(f"Failed to get search history: {e}")
            return []
    
    def get_search_summary(self, session_id: str = None) -> Dict:
        """
        Get search summary for sidebar display
        """
        try:
            return self.db_manager.get_search_summary(session_id)
        except Exception as e:
            print(f"Failed to get search summary: {e}")
            return {
                "total_searches": 0,
                "unique_queries": 0,
                "recent_searches": 0,
                "common_queries": []
            }
    
    def get_recent_products_for_recommendations(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Get recent products for a query to use in recommendations
        This allows the agent to suggest products from past searches
        """
        try:
            return self.db_manager.get_recent_products_for_query(query, limit)
        except Exception as e:
            print(f"Failed to get recent products for recommendations: {e}")
            return []
    
    def clear_search_history(self, session_id: str = None):
        """Clear search history"""
        try:
            self.db_manager.clear_search_history(session_id)
        except Exception as e:
            print(f"Failed to clear search history: {e}")
    
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
        """Get all products from the database with caching"""
        cache_key = self._get_cache_key("get_all_products")
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        try:
            products = self.db_manager.get_all_products()
            # Only log once per cache period instead of every call
            if not cached_result:
                print(f"Retrieved {len(products)} products from database (cached for 30s)")
            self._set_cache(cache_key, products)
            return products
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
    
    def search_mercari_real_time(self, query: str, filters: Dict[str, Any] = None, session_id: str = None) -> List[Dict]:
        """
        Perform real-time search on Mercari Japan
        Returns fresh data from the website and stores in history
        """
        if not query:
            return []
        
        if not self.use_real_data or not self.scraper:
            print("Real-time search not available, using database")
            return self.search_products(query, filters or {}, session_id)
        
        try:
            products = self.scraper.search_products(query, filters or {})
            print(f"Real-time search found {len(products)} products")
            
            # Store results in history
            if products and session_id:
                try:
                    self.db_manager.store_search_results(query, products, session_id)
                except Exception as e:
                    print(f"Failed to store real-time search results: {e}")
            
            return products
        except Exception as e:
            print(f"Real-time search failed: {e}, falling back to database")
            return self.search_products(query, filters or {}, session_id)
    
    def search_with_ranking(self, query: str, filters: Dict[str, Any] = None, session_id: str = None) -> List[Dict]:
        """
        Search products and apply ranking
        """
        from core.product_ranker import ProductRanker
        
        # Get products with history fallback
        products = self.search_with_history_fallback(query, filters, session_id)
        
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
        """Get products by category with caching"""
        cache_key = self._get_cache_key("get_products_by_category", category)
        cached_result = self._get_from_cache(cache_key)
        
        if cached_result is not None:
            return cached_result
        
        try:
            all_products = self.get_all_products()
            category_products = [
                p for p in all_products 
                if p.get('category', '').lower() == category.lower()
            ]
            self._set_cache(cache_key, category_products)
            return category_products
        except Exception as e:
            print(f"Error getting products by category: {e}")
            return []
    
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
