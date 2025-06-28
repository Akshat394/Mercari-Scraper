import pytest
from unittest.mock import Mock, patch
from core.translator import Translator

class TestTranslator:
    """Test suite for Translator"""
    
    @pytest.fixture
    def mock_llm_service(self):
        """Create mock LLM service for testing"""
        return Mock()
    
    @pytest.fixture
    def translator(self, mock_llm_service):
        """Create Translator instance for testing"""
        return Translator(mock_llm_service)
    
    def test_translator_initialization(self, translator, mock_llm_service):
        """Test Translator initializes correctly"""
        assert translator.llm_service == mock_llm_service
    
    @patch('core.translator.detect')
    def test_detect_language_english(self, mock_detect, translator):
        """Test language detection for English"""
        mock_detect.return_value.lang = 'en'
        
        result = translator.detect_language("I want to buy an iPhone")
        
        assert result == 'en'
        mock_detect.assert_called_once_with("I want to buy an iPhone")
    
    @patch('core.translator.detect')
    def test_detect_language_japanese(self, mock_detect, translator):
        """Test language detection for Japanese"""
        mock_detect.return_value.lang = 'ja'
        
        result = translator.detect_language("iPhoneが欲しいです")
        
        assert result == 'ja'
        mock_detect.assert_called_once_with("iPhoneが欲しいです")
    
    @patch('core.translator.detect')
    def test_detect_language_unknown(self, mock_detect, translator):
        """Test language detection for unknown language"""
        mock_detect.return_value.lang = 'unknown'
        
        result = translator.detect_language("Some unknown text")
        
        assert result == 'en'  # Default to English
    
    @patch('core.translator.detect')
    def test_detect_language_error(self, mock_detect, translator):
        """Test language detection error handling"""
        mock_detect.side_effect = Exception("Detection failed")
        
        result = translator.detect_language("Some text")
        
        assert result == 'en'  # Default to English on error
    
    @patch('core.translator.LLMService')
    def test_translate_to_japanese_success(self, mock_llm_class, translator):
        """Test successful translation to Japanese"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "iPhoneを探しています"
        
        translator.llm_service.client.chat.completions.create.return_value = mock_response
        
        result = translator.translate_to_japanese("I'm looking for an iPhone", {})
        
        assert result == "iPhoneを探しています"
        translator.llm_service.client.chat.completions.create.assert_called_once()
    
    @patch('core.translator.LLMService')
    def test_translate_to_japanese_error(self, mock_llm_class, translator):
        """Test translation to Japanese error handling"""
        translator.llm_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        result = translator.translate_to_japanese("I'm looking for an iPhone", {})
        
        # Should return original text on error
        assert result == "I'm looking for an iPhone"
    
    @patch('core.translator.LLMService')
    def test_translate_to_japanese_with_context(self, mock_llm_class, translator):
        """Test translation to Japanese with context"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "iPhone 15を探しています"
        
        translator.llm_service.client.chat.completions.create.return_value = mock_response
        
        context = {"product_keywords": ["iPhone 15"], "category": "Electronics"}
        result = translator.translate_to_japanese("I'm looking for an iPhone 15", context)
        
        assert result == "iPhone 15を探しています"
        translator.llm_service.client.chat.completions.create.assert_called_once()
    
    @patch('core.translator.LLMService')
    def test_translate_to_english_success(self, mock_llm_class, translator):
        """Test successful translation to English"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "I'm looking for an iPhone"
        
        translator.llm_service.client.chat.completions.create.return_value = mock_response
        
        result = translator.translate_to_english("iPhoneを探しています")
        
        assert result == "I'm looking for an iPhone"
        translator.llm_service.client.chat.completions.create.assert_called_once()
    
    @patch('core.translator.LLMService')
    def test_translate_to_english_error(self, mock_llm_class, translator):
        """Test translation to English error handling"""
        translator.llm_service.client.chat.completions.create.side_effect = Exception("API Error")
        
        result = translator.translate_to_english("iPhoneを探しています")
        
        # Should return original text on error
        assert result == "iPhoneを探しています"
    
    def test_translate_query_english_to_japanese(self, translator):
        """Test query translation from English to Japanese"""
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.return_value = "iPhoneを探しています"
            
            result = translator.translate_query("I'm looking for an iPhone", "en", "ja")
            
            assert result == "iPhoneを探しています"
            mock_translate.assert_called_once_with("I'm looking for an iPhone", {})
    
    def test_translate_query_japanese_to_english(self, translator):
        """Test query translation from Japanese to English"""
        with patch.object(translator, 'translate_to_english') as mock_translate:
            mock_translate.return_value = "I'm looking for an iPhone"
            
            result = translator.translate_query("iPhoneを探しています", "ja", "en")
            
            assert result == "I'm looking for an iPhone"
            mock_translate.assert_called_once_with("iPhoneを探しています")
    
    def test_translate_query_same_language(self, translator):
        """Test query translation when source and target are the same"""
        result = translator.translate_query("I'm looking for an iPhone", "en", "en")
        
        assert result == "I'm looking for an iPhone"
    
    def test_translate_query_with_context(self, translator):
        """Test query translation with context"""
        context = {"product_keywords": ["iPhone 15"], "category": "Electronics"}
        
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.return_value = "iPhone 15を探しています"
            
            result = translator.translate_query("I'm looking for an iPhone 15", "en", "ja", context)
            
            assert result == "iPhone 15を探しています"
            mock_translate.assert_called_once_with("I'm looking for an iPhone 15", context)
    
    def test_translate_product_data_english_to_japanese(self, translator):
        """Test product data translation from English to Japanese"""
        product_data = {
            "name": "iPhone 15",
            "description": "Brand new iPhone 15",
            "category": "Electronics"
        }
        
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.side_effect = ["iPhone 15", "新品のiPhone 15", "Electronics"]
            
            result = translator.translate_product_data(product_data, "en", "ja")
            
            expected = {
                "name": "iPhone 15",
                "description": "新品のiPhone 15", 
                "category": "Electronics"
            }
            assert result == expected
            assert mock_translate.call_count == 2  # Only description and name should be translated
    
    def test_translate_product_data_japanese_to_english(self, translator):
        """Test product data translation from Japanese to English"""
        product_data = {
            "name": "iPhone 15",
            "description": "新品のiPhone 15",
            "category": "Electronics"
        }
        
        with patch.object(translator, 'translate_to_english') as mock_translate:
            mock_translate.side_effect = ["iPhone 15", "Brand new iPhone 15"]
            
            result = translator.translate_product_data(product_data, "ja", "en")
            
            expected = {
                "name": "iPhone 15",
                "description": "Brand new iPhone 15",
                "category": "Electronics"
            }
            assert result == expected
            assert mock_translate.call_count == 2
    
    def test_translate_product_data_no_translation_needed(self, translator):
        """Test product data translation when no translation is needed"""
        product_data = {
            "name": "iPhone 15",
            "description": "Brand new iPhone 15",
            "category": "Electronics"
        }
        
        result = translator.translate_product_data(product_data, "en", "en")
        
        assert result == product_data
    
    def test_translate_product_data_error_handling(self, translator):
        """Test product data translation error handling"""
        product_data = {
            "name": "iPhone 15",
            "description": "Brand new iPhone 15",
            "category": "Electronics"
        }
        
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.side_effect = Exception("Translation failed")
            
            result = translator.translate_product_data(product_data, "en", "ja")
            
            # Should return original data on error
            assert result == product_data
    
    def test_translate_list_english_to_japanese(self, translator):
        """Test list translation from English to Japanese"""
        items = ["iPhone", "Samsung", "Nike"]
        
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.side_effect = ["iPhone", "Samsung", "Nike"]
            
            result = translator.translate_list(items, "en", "ja")
            
            assert result == ["iPhone", "Samsung", "Nike"]
            assert mock_translate.call_count == 3
    
    def test_translate_list_japanese_to_english(self, translator):
        """Test list translation from Japanese to English"""
        items = ["iPhone", "サムスン", "ナイキ"]
        
        with patch.object(translator, 'translate_to_english') as mock_translate:
            mock_translate.side_effect = ["iPhone", "Samsung", "Nike"]
            
            result = translator.translate_list(items, "ja", "en")
            
            assert result == ["iPhone", "Samsung", "Nike"]
            assert mock_translate.call_count == 3
    
    def test_translate_list_empty(self, translator):
        """Test list translation with empty list"""
        result = translator.translate_list([], "en", "ja")
        
        assert result == []
    
    def test_translate_list_error_handling(self, translator):
        """Test list translation error handling"""
        items = ["iPhone", "Samsung"]
        
        with patch.object(translator, 'translate_to_japanese') as mock_translate:
            mock_translate.side_effect = Exception("Translation failed")
            
            result = translator.translate_list(items, "en", "ja")
            
            # Should return original items on error
            assert result == items 