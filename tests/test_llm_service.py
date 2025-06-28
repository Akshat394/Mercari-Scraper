import pytest
import json
from unittest.mock import Mock, patch
from core.llm_service import LLMService

class TestLLMService:
    """Test suite for LLMService"""
    
    @pytest.fixture
    def llm_service(self):
        """Create LLMService instance for testing"""
        return LLMService()
    
    @pytest.fixture
    def mock_openai_response(self):
        """Mock OpenAI response for testing"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = '{"product_keywords": ["iphone"], "category": "Electronics"}'
        return mock_response
    
    def test_llm_service_initialization(self, llm_service):
        """Test LLMService initializes correctly"""
        assert llm_service.model == "gpt-4o"
        assert llm_service.client is not None
    
    @patch('core.llm_service.OpenAI')
    def test_parse_query_success(self, mock_openai, llm_service, mock_openai_response):
        """Test successful query parsing"""
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_openai_response
        mock_openai.return_value = mock_client
        
        result = llm_service.parse_query("I want an iPhone", "en")
        
        assert isinstance(result, dict)
        assert "product_keywords" in result
        assert "category" in result
        assert result["product_keywords"] == ["iphone"]
        assert result["category"] == "Electronics"
    
    @patch('core.llm_service.OpenAI')
    def test_parse_query_fallback(self, mock_openai, llm_service):
        """Test query parsing fallback when API fails"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        result = llm_service.parse_query("I want an iPhone", "en")
        
        assert isinstance(result, dict)
        assert "product_keywords" in result
        assert result["product_keywords"] == ["i want an iphone"]
    
    @patch('core.llm_service.OpenAI')
    def test_generate_recommendations_with_products(self, mock_openai, llm_service):
        """Test recommendation generation with products"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Here are great iPhone options for you!"
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        products = [
            {
                "name": "iPhone 15",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.5,
                "category": "Electronics"
            }
        ]
        
        result = llm_service.generate_recommendations("I want an iPhone", products, "en")
        
        assert isinstance(result, str)
        assert "iPhone" in result
    
    def test_generate_recommendations_no_products(self, llm_service):
        """Test recommendation generation with no products"""
        result = llm_service.generate_recommendations("I want an iPhone", [], "en")
        
        assert isinstance(result, str)
        assert "couldn't find" in result.lower()
    
    @patch('core.llm_service.OpenAI')
    def test_call_with_tools_success(self, mock_openai, llm_service):
        """Test successful tool calling"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "Tool call successful"
        mock_response.choices[0].message.tool_calls = []
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        messages = [{"role": "user", "content": "Search for iPhone"}]
        tools = [{"name": "search_mercari", "description": "Search Mercari"}]
        
        result = llm_service.call_with_tools(messages, tools)
        
        assert isinstance(result, dict)
        assert "content" in result
        assert "tool_calls" in result
        assert "model" in result
        assert result["content"] == "Tool call successful"
    
    @patch('core.llm_service.OpenAI')
    def test_call_with_tools_error(self, mock_openai, llm_service):
        """Test tool calling error handling"""
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_openai.return_value = mock_client
        
        messages = [{"role": "user", "content": "Search for iPhone"}]
        tools = [{"name": "search_mercari", "description": "Search Mercari"}]
        
        result = llm_service.call_with_tools(messages, tools)
        
        assert isinstance(result, dict)
        assert result["content"] == "Error processing request"
        assert result["tool_calls"] is None
    
    def test_parse_query_japanese(self, llm_service):
        """Test query parsing with Japanese input"""
        with patch.object(llm_service.client.chat.completions, 'create') as mock_create:
            mock_response = Mock()
            mock_response.choices = [Mock()]
            mock_response.choices[0].message = Mock()
            mock_response.choices[0].message.content = '{"product_keywords": ["iPhone"], "category": "Electronics"}'
            mock_create.return_value = mock_response
            
            result = llm_service.parse_query("iPhoneが欲しい", "ja")
            
            assert isinstance(result, dict)
            assert "product_keywords" in result
            assert result["product_keywords"] == ["iPhone"]
            assert result["category"] == "Electronics" 