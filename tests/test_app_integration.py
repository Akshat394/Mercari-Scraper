import pytest
import streamlit as st
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestAppIntegration:
    """Test suite for main app integration"""
    
    @pytest.fixture
    def mock_streamlit(self):
        """Mock Streamlit components"""
        with patch('streamlit.set_page_config') as mock_config:
            with patch('streamlit.title') as mock_title:
                with patch('streamlit.markdown') as mock_markdown:
                    with patch('streamlit.sidebar') as mock_sidebar:
                        with patch('streamlit.chat_input') as mock_chat_input:
                            with patch('streamlit.chat_message') as mock_chat_message:
                                with patch('streamlit.spinner') as mock_spinner:
                                    with patch('streamlit.error') as mock_error:
                                        with patch('streamlit.info') as mock_info:
                                            with patch('streamlit.tabs') as mock_tabs:
                                                with patch('streamlit.columns') as mock_columns:
                                                    with patch('streamlit.image') as mock_image:
                                                        yield {
                                                            'config': mock_config,
                                                            'title': mock_title,
                                                            'markdown': mock_markdown,
                                                            'sidebar': mock_sidebar,
                                                            'chat_input': mock_chat_input,
                                                            'chat_message': mock_chat_message,
                                                            'spinner': mock_spinner,
                                                            'error': mock_error,
                                                            'info': mock_info,
                                                            'tabs': mock_tabs,
                                                            'columns': mock_columns,
                                                            'image': mock_image
                                                        }
    
    @pytest.fixture
    def mock_services(self):
        """Mock all services"""
        with patch('app.LLMService') as mock_llm:
            with patch('app.DataHandler') as mock_data:
                with patch('app.ProductRanker') as mock_ranker:
                    with patch('app.Translator') as mock_translator:
                        yield {
                            'llm': mock_llm,
                            'data': mock_data,
                            'ranker': mock_ranker,
                            'translator': mock_translator
                        }
    
    def test_app_initialization(self, mock_streamlit, mock_services):
        """Test app initializes correctly"""
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (
                mock_services['llm'].return_value,
                mock_services['data'].return_value,
                mock_services['ranker'].return_value,
                mock_services['translator'].return_value
            )
            
            # Import and run main function
            from app import main
            
            # Should not raise any exceptions
            main()
            
            # Verify key components were called
            mock_streamlit['title'].assert_called_once()
            mock_streamlit['markdown'].assert_called()
    
    def test_app_with_user_input(self, mock_streamlit, mock_services):
        """Test app with user input"""
        # Mock user input
        mock_streamlit['chat_input'].return_value = "I want an iPhone"
        
        # Mock services
        mock_llm = mock_services['llm'].return_value
        mock_data = mock_services['data'].return_value
        mock_ranker = mock_services['ranker'].return_value
        mock_translator = mock_services['translator'].return_value
        
        # Mock service responses
        mock_llm.parse_query.return_value = {
            "product_keywords": ["iPhone"],
            "category": "Electronics",
            "price_range": {"min": 100000, "max": 200000},
            "condition": "new",
            "brand": "Apple"
        }
        
        mock_data.search_products.return_value = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics",
                "brand": "Apple"
            }
        ]
        
        mock_ranker.rank_products.return_value = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics",
                "brand": "Apple"
            }
        ]
        
        mock_llm.generate_recommendations.return_value = "Here are great iPhone options!"
        mock_translator.translate_to_japanese.return_value = "iPhoneを探しています"
        
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (mock_llm, mock_data, mock_ranker, mock_translator)
            
            from app import main
            main()
            
            # Verify services were called
            mock_llm.parse_query.assert_called()
            mock_data.search_products.assert_called()
            mock_ranker.rank_products.assert_called()
            mock_llm.generate_recommendations.assert_called()
    
    def test_app_error_handling(self, mock_streamlit, mock_services):
        """Test app error handling"""
        # Mock service initialization failure
        with patch('app.initialize_services') as mock_init:
            mock_init.side_effect = Exception("Service initialization failed")
            
            from app import main
            
            # Should handle error gracefully
            main()
            
            # Verify error was displayed
            mock_streamlit['error'].assert_called()
    
    def test_app_real_time_toggle(self, mock_streamlit, mock_services):
        """Test real-time toggle functionality"""
        # Mock sidebar checkbox
        mock_checkbox = Mock()
        mock_checkbox.return_value = True
        mock_streamlit['sidebar'].checkbox = mock_checkbox
        
        # Mock services
        mock_data = mock_services['data'].return_value
        mock_data.search_mercari_real_time.return_value = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics"
            }
        ]
        
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (
                mock_services['llm'].return_value,
                mock_data,
                mock_services['ranker'].return_value,
                mock_services['translator'].return_value
            )
            
            from app import main
            main()
            
            # Verify real-time search was called
            mock_data.search_mercari_real_time.assert_called()
    
    def test_app_language_detection(self, mock_streamlit, mock_services):
        """Test language detection functionality"""
        # Mock user input in Japanese
        mock_streamlit['chat_input'].return_value = "iPhoneが欲しい"
        
        # Mock services
        mock_translator = mock_services['translator'].return_value
        mock_translator.detect_language.return_value = "ja"
        
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (
                mock_services['llm'].return_value,
                mock_services['data'].return_value,
                mock_services['ranker'].return_value,
                mock_translator
            )
            
            from app import main
            main()
            
            # Verify language detection was used
            mock_translator.detect_language.assert_called()
    
    def test_app_product_showcase(self, mock_streamlit, mock_services):
        """Test product showcase functionality"""
        # Mock data handler
        mock_data = mock_services['data'].return_value
        mock_data.get_all_products.return_value = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics"
            }
        ]
        
        # Mock tabs
        mock_tab1 = Mock()
        mock_tab2 = Mock()
        mock_tab3 = Mock()
        mock_tab4 = Mock()
        mock_streamlit['tabs'].return_value = [mock_tab1, mock_tab2, mock_tab3, mock_tab4]
        
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (
                mock_services['llm'].return_value,
                mock_data,
                mock_services['ranker'].return_value,
                mock_services['translator'].return_value
            )
            
            from app import main
            main()
            
            # Verify product showcase was called
            mock_data.get_all_products.assert_called()
    
    def test_app_chat_history(self, mock_streamlit, mock_services):
        """Test chat history functionality"""
        # Mock session state
        with patch('streamlit.session_state') as mock_session:
            mock_session.messages = [
                {"role": "user", "content": "I want an iPhone"},
                {"role": "assistant", "content": "Here are some options", "products": []}
            ]
            
            with patch('app.initialize_services') as mock_init:
                mock_init.return_value = (
                    mock_services['llm'].return_value,
                    mock_services['data'].return_value,
                    mock_services['ranker'].return_value,
                    mock_services['translator'].return_value
                )
                
                from app import main
                main()
                
                # Verify chat history was displayed
                mock_streamlit['chat_message'].assert_called()
    
    def test_app_no_user_input(self, mock_streamlit, mock_services):
        """Test app behavior when no user input"""
        # Mock no user input
        mock_streamlit['chat_input'].return_value = None
        
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (
                mock_services['llm'].return_value,
                mock_services['data'].return_value,
                mock_services['ranker'].return_value,
                mock_services['translator'].return_value
            )
            
            from app import main
            main()
            
            # Should not call services when no input
            mock_services['llm'].return_value.parse_query.assert_not_called()
    
    def test_app_service_caching(self, mock_streamlit, mock_services):
        """Test service caching functionality"""
        with patch('app.initialize_services') as mock_init:
            mock_init.return_value = (
                mock_services['llm'].return_value,
                mock_services['data'].return_value,
                mock_services['ranker'].return_value,
                mock_services['translator'].return_value
            )
            
            from app import main
            
            # Call main twice
            main()
            main()
            
            # Should only initialize services once due to caching
            assert mock_init.call_count == 1
    
    def test_app_display_product_card(self, mock_streamlit):
        """Test product card display functionality"""
        from app import display_product_card
        
        product = {
            "id": "1",
            "name": "iPhone 15 Pro",
            "price": 150000,
            "condition": "new",
            "seller_rating": 4.8,
            "category": "Electronics",
            "brand": "Apple",
            "image_url": "https://example.com/iphone.jpg"
        }
        
        # Mock columns
        mock_col1 = Mock()
        mock_col2 = Mock()
        mock_streamlit['columns'].return_value = [mock_col1, mock_col2]
        
        display_product_card(product)
        
        # Verify product card was displayed
        mock_streamlit['columns'].assert_called_once()
    
    def test_app_display_products(self, mock_streamlit):
        """Test products display functionality"""
        from app import display_products
        
        products = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics"
            }
        ]
        
        display_products(products)
        
        # Verify products were displayed
        mock_streamlit['markdown'].assert_called()
    
    def test_app_display_products_empty(self, mock_streamlit):
        """Test products display with empty list"""
        from app import display_products
        
        display_products([])
        
        # Verify info message was displayed
        mock_streamlit['info'].assert_called_once()
    
    def test_app_get_showcase_products(self, mock_services):
        """Test showcase products functionality"""
        from app import get_showcase_products
        
        mock_data = mock_services['data'].return_value
        mock_data.get_all_products.return_value = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics"
            }
        ]
        
        result = get_showcase_products(mock_data, "Electronics")
        
        assert len(result) == 1
        assert result[0]["category"] == "Electronics"
    
    def test_app_display_showcase_grid(self, mock_streamlit):
        """Test showcase grid display functionality"""
        from app import display_showcase_grid
        
        products = [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics"
            }
        ]
        
        display_showcase_grid(products)
        
        # Verify grid was displayed
        mock_streamlit['markdown'].assert_called()
    
    def test_app_display_showcase_grid_empty(self, mock_streamlit):
        """Test showcase grid display with empty products"""
        from app import display_showcase_grid
        
        display_showcase_grid([])
        
        # Verify info message was displayed
        mock_streamlit['info'].assert_called_once() 