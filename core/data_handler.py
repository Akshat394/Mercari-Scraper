from typing import Dict, List, Any, Optional
from core.database import DatabaseManager

class DataHandler:
    """Handles data retrieval and processing for Mercari products"""
    
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def search_products(self, query: str, filters: Dict[str, Any]) -> List[Dict]:
        """
        Search for products based on query and filters
        Uses database for persistent storage
        """
        return self.db_manager.search_products(query, filters)
    
    def get_product_details(self, product_id: str) -> Optional[Dict]:
        """Get detailed information for a specific product"""
        return self.db_manager.get_product_by_id(product_id)
    
    def add_product(self, product_data: Dict) -> bool:
        """Add a new product to the database"""
        return self.db_manager.add_product(product_data)
    
    def get_all_products(self) -> List[Dict]:
        """Get all products from the database"""
        return self.db_manager.get_all_products()
