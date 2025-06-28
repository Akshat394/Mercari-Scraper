import streamlit as st
import os
import json
from typing import Dict, List, Optional
from core.llm_service import LLMService
from core.data_handler import DataHandler
from core.product_ranker import ProductRanker
from core.translator import Translator
from utils.helpers import detect_language, format_product_display

# Page configuration
st.set_page_config(
    page_title="Mercari Japan Shopping Assistant",
    page_icon="🛍️",
    layout="wide"
)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize all services with caching"""
    llm_service = LLMService()
    data_handler = DataHandler()
    product_ranker = ProductRanker()
    translator = Translator(llm_service)
    return llm_service, data_handler, product_ranker, translator

# Main application
def main():
    st.title("🛍️ Mercari Japan Shopping Assistant")
    st.markdown("Ask me about products you want to buy on Mercari Japan in English or Japanese!")
    
    # Initialize services
    try:
        llm_service, data_handler, product_ranker, translator = initialize_services()
    except Exception as e:
        st.error(f"Failed to initialize services: {str(e)}")
        st.stop()
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and "products" in message:
                st.markdown(message["content"])
                display_products(message["products"])
            else:
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("What would you like to buy on Mercari Japan?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process the query
        with st.chat_message("assistant"):
            with st.spinner("Searching for products..."):
                try:
                    # Detect language
                    user_language = detect_language(prompt)
                    
                    # Parse the query using LLM
                    query_data = llm_service.parse_query(prompt, user_language)
                    
                    # Translate to Japanese if needed
                    japanese_query = translator.translate_to_japanese(prompt, query_data) if user_language == 'en' else prompt
                    
                    # Search for products
                    products = data_handler.search_products(japanese_query, query_data)
                    
                    # Rank products
                    ranked_products = product_ranker.rank_products(products, query_data)
                    
                    # Get top 3 recommendations
                    top_products = ranked_products[:3]
                    
                    # Generate recommendations using LLM
                    recommendation = llm_service.generate_recommendations(
                        prompt, top_products, user_language
                    )
                    
                    # Display results
                    st.markdown(recommendation)
                    display_products(top_products)
                    
                    # Add to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": recommendation,
                        "products": top_products
                    })
                    
                except Exception as e:
                    error_msg = f"Sorry, I encountered an error while searching: {str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

def display_products(products: List[Dict]):
    """Display product recommendations in a formatted way"""
    if not products:
        st.info("No products found matching your criteria.")
        return
    
    for i, product in enumerate(products, 1):
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.image(product.get("image_url", "https://via.placeholder.com/150"), 
                        width=120)
            
            with col2:
                st.subheader(f"{i}. {product['name']}")
                st.write(f"**Price:** ¥{product['price']:,}")
                st.write(f"**Condition:** {product['condition']}")
                st.write(f"**Seller Rating:** {'⭐' * int(product['seller_rating'])} ({product['seller_rating']}/5)")
                if product.get('url'):
                    st.markdown(f"[View on Mercari]({product['url']})")
            
            st.divider()

if __name__ == "__main__":
    main()
