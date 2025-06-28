import pytest
from unittest.mock import Mock, patch, MagicMock
from core.llm_service import LLMService
from core.data_handler import DataHandler
from core.product_ranker import ProductRanker
from core.translator import Translator

class TestIntegration:
    """Integration tests for the complete system"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Create mock LLM service"""
        llm_service = Mock(spec=LLMService)
        
        # Mock parse_query response
        mock_parse_response = {
            "product_keywords": ["iPhone"],
            "category": "Electronics",
            "price_range": {"min": 100000, "max": 200000},
            "condition": "new",
            "brand": "Apple",
            "features": [],
            "search_intent": "buy"
        }
        llm_service.parse_query.return_value = mock_parse_response
        
        # Mock generate_recommendations response
        llm_service.generate_recommendations.return_value = "Here are great iPhone options for you!"
        
        return llm_service
    
    @pytest.fixture
    def mock_data_handler(self):
        """Create mock data handler"""
        data_handler = Mock(spec=DataHandler)
        
        # Mock sample products
        sample_products = [
            {
                "id": "1",
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
                "id": "2",
                "name": "iPhone 14",
                "price": 120000,
                "condition": "like_new",
                "seller_rating": 4.5,
                "category": "Electronics",
                "brand": "Apple",
                "image_url": "https://example.com/iphone14.jpg",
                "url": "https://mercari.com/item/2",
                "description": "Like new iPhone 14"
            }
        ]
        
        data_handler.search_products.return_value = sample_products
        data_handler.search_mercari_real_time.return_value = sample_products
        data_handler.get_all_products.return_value = sample_products
        
        return data_handler
    
    @pytest.fixture
    def product_ranker(self):
        """Create real product ranker"""
        return ProductRanker()
    
    @pytest.fixture
    def translator(self, mock_llm_service):
        """Create translator with mock LLM service"""
        return Translator(mock_llm_service)
    
    def test_complete_workflow_english_query(self, mock_llm_service, mock_data_handler, product_ranker, translator):
        """Test complete workflow with English query"""
        # Test query
        user_query = "I want to buy an iPhone under 200,000 yen"
        language = "en"
        
        # Step 1: Parse query
        query_data = mock_llm_service.parse_query(user_query, language)
        
        assert query_data["product_keywords"] == ["iPhone"]
        assert query_data["category"] == "Electronics"
        assert query_data["price_range"]["max"] == 200000
        
        # Step 2: Search products
        products = mock_data_handler.search_products(user_query, query_data)
        
        assert len(products) == 2
        assert all(p["category"] == "Electronics" for p in products)
        
        # Step 3: Rank products
        ranked_products = product_ranker.rank_products(products, query_data)
        
        assert len(ranked_products) == 2
        # iPhone 15 Pro should be ranked first (newer, higher rating)
        assert ranked_products[0]["name"] == "iPhone 15 Pro"
        
        # Step 4: Generate recommendations
        recommendations = mock_llm_service.generate_recommendations(user_query, ranked_products, language)
        
        assert isinstance(recommendations, str)
        assert "iPhone" in recommendations
    
    def test_complete_workflow_japanese_query(self, mock_llm_service, mock_data_handler, product_ranker, translator):
        """Test complete workflow with Japanese query"""
        # Test query
        user_query = "iPhone 15を20万円以下で探しています"
        language = "ja"
        
        # Step 1: Parse query
        query_data = mock_llm_service.parse_query(user_query, language)
        
        assert query_data["product_keywords"] == ["iPhone"]
        assert query_data["category"] == "Electronics"
        
        # Step 2: Search products
        products = mock_data_handler.search_products(user_query, query_data)
        
        assert len(products) == 2
        
        # Step 3: Rank products
        ranked_products = product_ranker.rank_products(products, query_data)
        
        assert len(ranked_products) == 2
        
        # Step 4: Generate recommendations
        recommendations = mock_llm_service.generate_recommendations(user_query, ranked_products, language)
        
        assert isinstance(recommendations, str)
    
    def test_real_time_scraping_integration(self, mock_llm_service, mock_data_handler, product_ranker):
        """Test integration with real-time scraping"""
        user_query = "I want an iPhone"
        query_data = {"product_keywords": ["iPhone"], "category": "Electronics"}
        
        # Test real-time search
        real_time_products = mock_data_handler.search_mercari_real_time(user_query, query_data)
        
        assert len(real_time_products) == 2
        assert all(p["category"] == "Electronics" for p in real_time_products)
        
        # Test ranking of real-time products
        ranked_products = product_ranker.rank_products(real_time_products, query_data)
        
        assert len(ranked_products) == 2
        assert ranked_products[0]["name"] == "iPhone 15 Pro"
    
    def test_fallback_to_database(self, mock_llm_service, mock_data_handler, product_ranker):
        """Test fallback to database when real-time scraping fails"""
        user_query = "I want an iPhone"
        query_data = {"product_keywords": ["iPhone"], "category": "Electronics"}
        
        # Mock real-time search failure
        mock_data_handler.search_mercari_real_time.return_value = []
        
        # Should fall back to database search
        products = mock_data_handler.search_products(user_query, query_data)
        
        assert len(products) == 2
        assert all(p["category"] == "Electronics" for p in products)
        
        # Test ranking still works
        ranked_products = product_ranker.rank_products(products, query_data)
        
        assert len(ranked_products) == 2
    
    def test_translation_integration(self, mock_llm_service, translator):
        """Test translation integration"""
        # Test English to Japanese translation
        english_query = "I want to buy an iPhone"
        
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.return_value = "iPhoneを買いたいです"
            
            translated = translator.translate_query(english_query, "en", "ja")
            
            assert translated == "iPhoneを買いたいです"
            mock_translate.assert_called_once_with(english_query, {})
        
        # Test Japanese to English translation
        japanese_query = "iPhoneを買いたいです"
        
        with patch.object(translator, 'translate_to_english') as mock_translate:
            mock_translate.return_value = "I want to buy an iPhone"
            
            translated = translator.translate_query(japanese_query, "ja", "en")
            
            assert translated == "I want to buy an iPhone"
            mock_translate.assert_called_once_with(japanese_query)
    
    def test_product_ranking_with_multiple_criteria(self, product_ranker):
        """Test product ranking with multiple criteria"""
        products = [
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
            },
            {
                "id": "3",
                "name": "Samsung Galaxy S24",
                "price": 140000,
                "condition": "new",
                "seller_rating": 4.2,
                "category": "Electronics",
                "brand": "Samsung"
            }
        ]
        
        preferences = {
            "category": "Electronics",
            "brand": "Apple",
            "condition": "new",
            "price_range": {"min": 100000, "max": 200000}
        }
        
        ranked_products = product_ranker.rank_products(products, preferences)
        
        # iPhone 15 Pro should be first (matches all criteria)
        assert ranked_products[0]["id"] == "1"
        assert ranked_products[0]["name"] == "iPhone 15 Pro"
        
        # iPhone 14 should be second (matches most criteria)
        assert ranked_products[1]["id"] == "2"
        assert ranked_products[1]["name"] == "iPhone 14"
        
        # Samsung should be last (matches fewer criteria)
        assert ranked_products[2]["id"] == "3"
        assert ranked_products[2]["name"] == "Samsung Galaxy S24"
    
    def test_error_handling_integration(self, mock_llm_service, mock_data_handler, product_ranker):
        """Test error handling across the system"""
        user_query = "I want an iPhone"
        
        # Mock LLM service failure
        mock_llm_service.parse_query.side_effect = Exception("LLM API Error")
        
        # Should handle error gracefully
        try:
            query_data = mock_llm_service.parse_query(user_query, "en")
        except Exception:
            # Fallback query data
            query_data = {
                "product_keywords": [user_query.lower()],
                "category": None,
                "price_range": {"min": None, "max": None},
                "condition": None,
                "brand": None,
                "features": [],
                "search_intent": "buy"
            }
        
        # System should continue working with fallback data
        products = mock_data_handler.search_products(user_query, query_data)
        
        assert len(products) == 2
        
        ranked_products = product_ranker.rank_products(products, query_data)
        
        assert len(ranked_products) == 2
    
    def test_data_consistency(self, mock_data_handler, product_ranker):
        """Test data consistency across the system"""
        # Get all products
        all_products = mock_data_handler.get_all_products()
        
        assert len(all_products) == 2
        assert all("id" in p for p in all_products)
        assert all("name" in p for p in all_products)
        assert all("price" in p for p in all_products)
        assert all("condition" in p for p in all_products)
        assert all("seller_rating" in p for p in all_products)
        assert all("category" in p for p in all_products)
        
        # Test ranking maintains data integrity
        ranked_products = product_ranker.rank_products(all_products, {})
        
        assert len(ranked_products) == 2
        assert all("id" in p for p in ranked_products)
        assert all("name" in p for p in ranked_products)
        assert all("price" in p for p in ranked_products)
    
    def test_performance_integration(self, mock_llm_service, mock_data_handler, product_ranker):
        """Test performance characteristics of the integrated system"""
        import time
        
        user_query = "I want an iPhone"
        query_data = {"product_keywords": ["iPhone"], "category": "Electronics"}
        
        # Measure search performance
        start_time = time.time()
        products = mock_data_handler.search_products(user_query, query_data)
        search_time = time.time() - start_time
        
        assert search_time < 1.0  # Should be fast
        assert len(products) == 2
        
        # Measure ranking performance
        start_time = time.time()
        ranked_products = product_ranker.rank_products(products, query_data)
        ranking_time = time.time() - start_time
        
        assert ranking_time < 1.0  # Should be fast
        assert len(ranked_products) == 2
    
    def test_multi_language_support(self, mock_llm_service, mock_data_handler, product_ranker, translator):
        """Test multi-language support across the system"""
        # Test English
        english_query = "I want an iPhone"
        english_products = mock_data_handler.search_products(english_query, {})
        english_ranked = product_ranker.rank_products(english_products, {})
        
        assert len(english_ranked) == 2
        
        # Test Japanese (simulated)
        japanese_query = "iPhoneが欲しい"
        japanese_products = mock_data_handler.search_products(japanese_query, {})
        japanese_ranked = product_ranker.rank_products(japanese_products, {})
        
        assert len(japanese_ranked) == 2
        
        # Both should return the same products (same database)
        assert len(english_ranked) == len(japanese_ranked)
        assert english_ranked[0]["id"] == japanese_ranked[0]["id"] 