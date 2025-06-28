import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.database import DatabaseManager, Product

class TestDatabaseManager:
    """Test suite for DatabaseManager"""
    
    @pytest.fixture
    def mock_engine(self):
        """Create mock database engine"""
        return Mock()
    
    @pytest.fixture
    def mock_session(self):
        """Create mock database session"""
        return Mock()
    
    @pytest.fixture
    def sample_product_data(self):
        """Sample product data for testing"""
        return {
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
        }
    
    @pytest.fixture
    def db_manager(self, mock_engine, mock_session):
        """Create DatabaseManager instance for testing"""
        with patch('core.database.create_engine', return_value=mock_engine):
            with patch('core.database.sessionmaker', return_value=mock_session):
                return DatabaseManager()
    
    def test_database_manager_initialization(self, db_manager, mock_engine, mock_session):
        """Test DatabaseManager initializes correctly"""
        assert db_manager.engine == mock_engine
        assert db_manager.SessionLocal == mock_session
    
    @patch('core.database.create_engine')
    def test_database_manager_with_connection_string(self, mock_create_engine):
        """Test DatabaseManager with connection string"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine
        
        connection_string = "postgresql://user:pass@localhost/test_db"
        db_manager = DatabaseManager(connection_string)
        
        assert db_manager.engine == mock_engine
        mock_create_engine.assert_called_once_with(connection_string)
    
    def test_create_tables(self, db_manager, mock_engine):
        """Test table creation"""
        db_manager.create_tables()
        
        mock_engine.create_all.assert_called_once()
    
    def test_add_product_success(self, db_manager, mock_session, sample_product_data):
        """Test successful product addition"""
        mock_session_instance = Mock()
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.add_product(sample_product_data)
        
        assert result is True
        mock_session_instance.add.assert_called_once()
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()
    
    def test_add_product_error(self, db_manager, mock_session, sample_product_data):
        """Test product addition error handling"""
        mock_session_instance = Mock()
        mock_session_instance.commit.side_effect = Exception("Database error")
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.add_product(sample_product_data)
        
        assert result is False
        mock_session_instance.rollback.assert_called_once()
        mock_session_instance.close.assert_called_once()
    
    def test_get_product_by_id_success(self, db_manager, mock_session, sample_product_data):
        """Test successful product retrieval by ID"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.first.return_value = mock_product
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_product_by_id("test_1")
        
        assert result == sample_product_data
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_get_product_by_id_not_found(self, db_manager, mock_session):
        """Test product retrieval when product not found"""
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.first.return_value = None
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_product_by_id("nonexistent")
        
        assert result is None
        mock_session_instance.close.assert_called_once()
    
    def test_get_all_products_success(self, db_manager, mock_session, sample_product_data):
        """Test successful retrieval of all products"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_all_products()
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_get_all_products_empty(self, db_manager, mock_session):
        """Test retrieval of all products when database is empty"""
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.all.return_value = []
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_all_products()
        
        assert result == []
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_by_name(self, db_manager, mock_session, sample_product_data):
        """Test product search by name"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        filters = {"name": "iPhone"}
        result = db_manager.search_products("iPhone", filters)
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_by_category(self, db_manager, mock_session, sample_product_data):
        """Test product search by category"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        filters = {"category": "Electronics"}
        result = db_manager.search_products("iPhone", filters)
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_by_price_range(self, db_manager, mock_session, sample_product_data):
        """Test product search by price range"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        filters = {"price_range": {"min": 100000, "max": 200000}}
        result = db_manager.search_products("iPhone", filters)
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_by_condition(self, db_manager, mock_session, sample_product_data):
        """Test product search by condition"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        filters = {"condition": "new"}
        result = db_manager.search_products("iPhone", filters)
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_multiple_filters(self, db_manager, mock_session, sample_product_data):
        """Test product search with multiple filters"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        filters = {
            "category": "Electronics",
            "condition": "new",
            "price_range": {"min": 100000, "max": 200000}
        }
        result = db_manager.search_products("iPhone", filters)
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_no_filters(self, db_manager, mock_session, sample_product_data):
        """Test product search without filters"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.search_products("iPhone", {})
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_search_products_error(self, db_manager, mock_session):
        """Test product search error handling"""
        mock_session_instance = Mock()
        mock_session_instance.query.side_effect = Exception("Database error")
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.search_products("iPhone", {})
        
        assert result == []
        mock_session_instance.close.assert_called_once()
    
    def test_populate_sample_data(self, db_manager, mock_session):
        """Test sample data population"""
        mock_session_instance = Mock()
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.populate_sample_data()
        
        assert result is True
        # Should add multiple products
        assert mock_session_instance.add.call_count > 0
        mock_session_instance.commit.assert_called_once()
        mock_session_instance.close.assert_called_once()
    
    def test_populate_sample_data_error(self, db_manager, mock_session):
        """Test sample data population error handling"""
        mock_session_instance = Mock()
        mock_session_instance.commit.side_effect = Exception("Database error")
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.populate_sample_data()
        
        assert result is False
        mock_session_instance.rollback.assert_called_once()
        mock_session_instance.close.assert_called_once()
    
    def test_get_products_by_category(self, db_manager, mock_session, sample_product_data):
        """Test getting products by category"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_products_by_category("Electronics")
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_get_products_by_brand(self, db_manager, mock_session, sample_product_data):
        """Test getting products by brand"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_products_by_brand("Apple")
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once()
    
    def test_get_products_in_price_range(self, db_manager, mock_session, sample_product_data):
        """Test getting products in price range"""
        mock_product = Mock()
        mock_product.to_dict.return_value = sample_product_data
        
        mock_session_instance = Mock()
        mock_session_instance.query.return_value.filter.return_value.all.return_value = [mock_product]
        db_manager.SessionLocal.return_value.__enter__.return_value = mock_session_instance
        
        result = db_manager.get_products_in_price_range(100000, 200000)
        
        assert result == [sample_product_data]
        mock_session_instance.query.assert_called_once_with(Product)
        mock_session_instance.close.assert_called_once() 