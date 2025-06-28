import pytest
import os
import sys
from unittest.mock import Mock, patch

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture(scope="session")
def sample_products():
    """Shared sample product data for all tests"""
    return [
        {
            "id": "test_1",
            "name": "iPhone 15 Pro",
            "price": 150000,
            "condition": "new",
            "seller_rating": 4.8,
            "category": "Electronics",
            "brand": "Apple",
            "image_url": "https://example.com/iphone.jpg",
            "url": "https://mercari.com/item/1",
            "description": "Brand new iPhone 15 Pro"
        },
        {
            "id": "test_2",
            "name": "iPhone 14",
            "price": 120000,
            "condition": "like_new",
            "seller_rating": 4.5,
            "category": "Electronics",
            "brand": "Apple",
            "image_url": "https://example.com/iphone14.jpg",
            "url": "https://mercari.com/item/2",
            "description": "Like new iPhone 14"
        },
        {
            "id": "test_3",
            "name": "Samsung Galaxy S24",
            "price": 140000,
            "condition": "new",
            "seller_rating": 4.2,
            "category": "Electronics",
            "brand": "Samsung",
            "image_url": "https://example.com/samsung.jpg",
            "url": "https://mercari.com/item/3",
            "description": "Brand new Samsung Galaxy S24"
        },
        {
            "id": "test_4",
            "name": "Nike Air Max",
            "price": 8000,
            "condition": "good",
            "seller_rating": 4.0,
            "category": "Fashion",
            "brand": "Nike",
            "image_url": "https://example.com/nike.jpg",
            "url": "https://mercari.com/item/4",
            "description": "Good condition Nike Air Max"
        }
    ]

@pytest.fixture(scope="session")
def mock_openai_response():
    """Shared mock OpenAI response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = '{"product_keywords": ["iphone"], "category": "Electronics"}'
    return mock_response

@pytest.fixture(scope="session")
def mock_database_session():
    """Shared mock database session"""
    return Mock()

@pytest.fixture(scope="session")
def mock_selenium_driver():
    """Shared mock Selenium driver"""
    return Mock()

@pytest.fixture(autouse=True)
def mock_environment_variables():
    """Mock environment variables for testing"""
    with patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-api-key',
        'DATABASE_URL': 'postgresql://test:test@localhost/test_db'
    }):
        yield

@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock external services to avoid actual API calls"""
    with patch('openai.OpenAI') as mock_openai:
        with patch('selenium.webdriver.Chrome') as mock_chrome:
            with patch('webdriver_manager.chrome.ChromeDriverManager') as mock_driver_manager:
                yield {
                    'openai': mock_openai,
                    'chrome': mock_chrome,
                    'driver_manager': mock_driver_manager
                }

@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing"""
    llm_service = Mock()
    
    # Mock parse_query response
    llm_service.parse_query.return_value = {
        "product_keywords": ["iPhone"],
        "category": "Electronics",
        "price_range": {"min": 100000, "max": 200000},
        "condition": "new",
        "brand": "Apple",
        "features": [],
        "search_intent": "buy"
    }
    
    # Mock generate_recommendations response
    llm_service.generate_recommendations.return_value = "Here are great iPhone options for you!"
    
    return llm_service

@pytest.fixture
def mock_data_handler():
    """Create a mock data handler for testing"""
    data_handler = Mock()
    
    # Mock sample products
    sample_products = [
        {
            "id": "1",
            "name": "iPhone 15 Pro",
            "price": 150000,
            "condition": "new",
            "seller_rating": 4.8,
            "category": "Electronics",
            "brand": "Apple"
        },
        {
            "id": "2",
            "name": "iPhone 14",
            "price": 120000,
            "condition": "like_new",
            "seller_rating": 4.5,
            "category": "Electronics",
            "brand": "Apple"
        }
    ]
    
    data_handler.search_products.return_value = sample_products
    data_handler.search_mercari_real_time.return_value = sample_products
    data_handler.get_all_products.return_value = sample_products
    data_handler.get_product_by_id.return_value = sample_products[0]
    data_handler.add_product.return_value = True
    
    return data_handler

@pytest.fixture
def real_product_ranker():
    """Create a real product ranker for testing"""
    from core.product_ranker import ProductRanker
    return ProductRanker()

@pytest.fixture
def mock_translator():
    """Create a mock translator for testing"""
    translator = Mock()
    
    translator.translate_to_japanese.return_value = "iPhoneを探しています"
    translator.translate_to_english.return_value = "I'm looking for an iPhone"
    translator.detect_language.return_value = "en"
    
    return translator

# Test markers
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )

# Test collection hooks
def pytest_collection_modifyitems(config, items):
    """Modify test collection"""
    for item in items:
        # Mark tests based on their location
        if "test_integration" in item.nodeid:
            item.add_marker(pytest.mark.integration)
        elif "test_unit" in item.nodeid:
            item.add_marker(pytest.mark.unit)
        
        # Mark slow tests
        if "test_performance" in item.nodeid or "test_scraping" in item.nodeid:
            item.add_marker(pytest.mark.slow)
        
        # Mark external service tests
        if "test_mercari_scraper" in item.nodeid or "test_openai" in item.nodeid:
            item.add_marker(pytest.mark.external) 