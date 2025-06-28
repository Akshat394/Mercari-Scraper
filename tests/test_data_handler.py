import pytest
from unittest.mock import Mock, patch, MagicMock
from core.data_handler import DataHandler

class TestDataHandler:
    """Test suite for DataHandler"""
    
    @pytest.fixture
    def data_handler(self):
        """Create DataHandler instance for testing"""
        return DataHandler()
    
    @pytest.fixture
    def sample_products(self):
        """Sample product data for testing"""
        return [
            {
                "id": "test_1",
                "name": "iPhone 15",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.5,
                "category": "Electronics",
                "brand": "Apple",
                "image_url": "https://example.com/iphone.jpg",
                "url": "https://mercari.com/item/1",
                "description": "Brand new iPhone 15"
            },
            {
                "id": "test_2", 
                "name": "Nike Shoes",
                "price": 8000,
                "condition": "good",
                "seller_rating": 4.2,
                "category": "Fashion",
                "brand": "Nike",
                "image_url": "https://example.com/shoes.jpg",
                "url": "https://mercari.com/item/2",
                "description": "Good condition Nike shoes"
            }
        ]
    
    def test_data_handler_initialization(self, data_handler):
        """Test DataHandler initializes correctly"""
        assert data_handler.db_manager is not None
        # Should have scraper if dependencies are available
        assert hasattr(data_handler, 'scraper')
        assert hasattr(data_handler, 'use_real_data')
    
    @patch('core.data_handler.MercariScraper')
    def test_search_products_with_real_data(self, mock_scraper_class, data_handler, sample_products):
        """Test product search with real scraper available"""
        # Mock the scraper
        mock_scraper = Mock()
        mock_scraper.search_products.return_value = sample_products
        mock_scraper_class.return_value = mock_scraper
        
        # Set up data handler to use real data
        data_handler.scraper = mock_scraper
        data_handler.use_real_data = True
        
        query = "iPhone"
        filters = {"category": "Electronics"}
        
        result = data_handler.search_products(query, filters)
        
        assert result == sample_products
        mock_scraper.search_products.assert_called_once_with(query, filters)
    
    @patch('core.data_handler.MercariScraper')
    def test_search_products_fallback_to_database(self, mock_scraper_class, data_handler, sample_products):
        """Test product search falls back to database when scraper fails"""
        # Mock the scraper to fail
        mock_scraper = Mock()
        mock_scraper.search_products.side_effect = Exception("Scraping failed")
        mock_scraper_class.return_value = mock_scraper
        
        # Mock database to return sample products
        data_handler.db_manager.search_products.return_value = sample_products
        
        # Set up data handler to use real data
        data_handler.scraper = mock_scraper
        data_handler.use_real_data = True
        
        query = "iPhone"
        filters = {"category": "Electronics"}
        
        result = data_handler.search_products(query, filters)
        
        assert result == sample_products
        data_handler.db_manager.search_products.assert_called_once_with(query, filters)
    
    def test_search_products_database_only(self, data_handler, sample_products):
        """Test product search uses database when real data is disabled"""
        # Mock database to return sample products
        data_handler.db_manager.search_products.return_value = sample_products
        data_handler.use_real_data = False
        
        query = "iPhone"
        filters = {"category": "Electronics"}
        
        result = data_handler.search_products(query, filters)
        
        assert result == sample_products
        data_handler.db_manager.search_products.assert_called_once_with(query, filters)
    
    @patch('core.data_handler.MercariScraper')
    def test_search_mercari_real_time_success(self, mock_scraper_class, data_handler, sample_products):
        """Test real-time Mercari search success"""
        # Mock the scraper
        mock_scraper = Mock()
        mock_scraper.search_products.return_value = sample_products
        mock_scraper_class.return_value = mock_scraper
        
        data_handler.scraper = mock_scraper
        data_handler.use_real_data = True
        
        query = "iPhone"
        filters = {"category": "Electronics"}
        
        result = data_handler.search_mercari_real_time(query, filters)
        
        assert result == sample_products
        mock_scraper.search_products.assert_called_once_with(query, filters)
    
    @patch('core.data_handler.MercariScraper')
    def test_search_mercari_real_time_failure(self, mock_scraper_class, data_handler):
        """Test real-time Mercari search failure"""
        # Mock the scraper to fail
        mock_scraper = Mock()
        mock_scraper.search_products.side_effect = Exception("Network error")
        mock_scraper_class.return_value = mock_scraper
        
        data_handler.scraper = mock_scraper
        data_handler.use_real_data = True
        
        query = "iPhone"
        filters = {"category": "Electronics"}
        
        result = data_handler.search_mercari_real_time(query, filters)
        
        assert result == []
    
    def test_search_mercari_real_time_no_scraper(self, data_handler):
        """Test real-time Mercari search when scraper is not available"""
        data_handler.scraper = None
        data_handler.use_real_data = False
        
        query = "iPhone"
        filters = {"category": "Electronics"}
        
        result = data_handler.search_mercari_real_time(query, filters)
        
        assert result == []
    
    def test_get_product_details(self, data_handler, sample_products):
        """Test getting product details"""
        product_id = "test_1"
        expected_product = sample_products[0]
        
        data_handler.db_manager.get_product_by_id.return_value = expected_product
        
        result = data_handler.get_product_details(product_id)
        
        assert result == expected_product
        data_handler.db_manager.get_product_by_id.assert_called_once_with(product_id)
    
    def test_add_product(self, data_handler, sample_products):
        """Test adding a product"""
        product_data = sample_products[0]
        
        data_handler.db_manager.add_product.return_value = True
        
        result = data_handler.add_product(product_data)
        
        assert result is True
        data_handler.db_manager.add_product.assert_called_once_with(product_data)
    
    def test_get_all_products(self, data_handler, sample_products):
        """Test getting all products"""
        data_handler.db_manager.get_all_products.return_value = sample_products
        
        result = data_handler.get_all_products()
        
        assert result == sample_products
        data_handler.db_manager.get_all_products.assert_called_once()
    
    def test_close(self, data_handler):
        """Test closing the data handler"""
        # Mock scraper
        mock_scraper = Mock()
        data_handler.scraper = mock_scraper
        
        data_handler.close()
        
        mock_scraper.close.assert_called_once()
    
    def test_close_no_scraper(self, data_handler):
        """Test closing when no scraper is available"""
        data_handler.scraper = None
        
        # Should not raise an exception
        data_handler.close()
    
    @patch('core.data_handler.MercariScraper')
    def test_real_data_initialization_success(self, mock_scraper_class):
        """Test successful initialization with real scraper"""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper
        
        data_handler = DataHandler()
        
        assert data_handler.scraper == mock_scraper
        assert data_handler.use_real_data is True
    
    @patch('core.data_handler.MercariScraper')
    def test_real_data_initialization_failure(self, mock_scraper_class):
        """Test initialization when scraper import fails"""
        mock_scraper_class.side_effect = ImportError("Module not found")
        
        data_handler = DataHandler()
        
        assert data_handler.scraper is None
        assert data_handler.use_real_data is False 