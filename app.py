import streamlit as st
import os
import json
import time
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
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for enhanced UI
st.markdown("""
<style>
    /* Main theme colors */
    :root {
        --primary-color: #ff6b6b;
        --secondary-color: #4ecdc4;
        --accent-color: #45b7d1;
        --bg-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --card-bg: rgba(255, 255, 255, 0.95);
        --text-color: #2c3e50;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main > div {
        background: var(--bg-gradient);
        padding: 1rem;
        border-radius: 15px;
    }
    
    /* Chat container */
    .stChatMessage {
        background: var(--card-bg);
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
        margin: 10px 0;
        animation: slideInUp 0.5s ease-out;
    }
    
    /* Product showcase section */
    .product-showcase {
        background: var(--card-bg);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Product cards */
    .product-card {
        background: linear-gradient(145deg, #ffffff, #f0f0f0);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem;
        box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .product-card:hover {
        transform: translateY(-10px) scale(1.02);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.2);
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, var(--primary-color), var(--secondary-color), var(--accent-color));
        opacity: 0;
        transition: opacity 0.3s ease;
    }
    
    .product-card:hover::before {
        opacity: 1;
    }
    
    /* Product images */
    .product-image {
        border-radius: 12px;
        transition: transform 0.3s ease;
        border: 2px solid rgba(255, 255, 255, 0.5);
    }
    
    .product-image:hover {
        transform: scale(1.05);
    }
    
    /* Category pills */
    .category-pill {
        display: inline-block;
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
    }
    
    /* Price styling */
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: var(--primary-color);
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Star ratings */
    .star-rating {
        color: #ffd700;
        font-size: 1.2rem;
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }
    
    /* Animations */
    @keyframes slideInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    @keyframes fadeInScale {
        from {
            opacity: 0;
            transform: scale(0.8);
        }
        to {
            opacity: 1;
            transform: scale(1);
        }
    }
    
    /* Section headers */
    .section-header {
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(45deg, var(--primary-color), var(--accent-color));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        animation: fadeInScale 1s ease-out;
    }
    
    /* Chat input styling */
    .stChatInput > div > div {
        border-radius: 25px;
        border: 2px solid var(--secondary-color);
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, var(--primary-color), var(--secondary-color));
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        animation: pulse 0.6s ease-in-out;
    }
    
    /* Loading spinner */
    .stSpinner > div {
        border-color: var(--primary-color) !important;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: var(--bg-gradient);
    }
</style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def initialize_services():
    """Initialize all services with caching"""
    llm_service = LLMService()
    data_handler = DataHandler()
    product_ranker = ProductRanker()
    translator = Translator(llm_service)
    return llm_service, data_handler, product_ranker, translator

def display_products(products: List[Dict]):
    """Display product recommendations in a formatted way"""
    if not products:
        st.info("No products found matching your criteria.")
        return
    
    for i, product in enumerate(products, 1):
        # Create animated product card
        st.markdown(f"""
        <div class="product-card" style="animation-delay: {i*0.1}s;">
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns([1, 3])
            
            with col1:
                st.markdown(f"""
                <img src="{product.get('image_url', 'https://via.placeholder.com/150')}" 
                     class="product-image" 
                     style="width: 120px; height: 120px; object-fit: cover;">
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <h3 style="color: var(--text-color); margin-bottom: 1rem;">
                    {i}. {product['name']}
                </h3>
                """, unsafe_allow_html=True)
                
                # Category pill
                st.markdown(f"""
                <span class="category-pill">{product['category']}</span>
                """, unsafe_allow_html=True)
                
                # Price with styling
                st.markdown(f"""
                <div class="price-tag">¥{product['price']:,}</div>
                """, unsafe_allow_html=True)
                
                # Condition and rating
                st.markdown(f"""
                <div style="margin: 1rem 0;">
                    <strong>Condition:</strong> {product['condition'].title()}<br>
                    <span class="star-rating">{'⭐' * int(product['seller_rating'])}</span> 
                    <strong>({product['seller_rating']}/5)</strong>
                </div>
                """, unsafe_allow_html=True)
                
                if product.get('url'):
                    st.markdown(f"""
                    <a href="{product['url']}" target="_blank" 
                       style="display: inline-block; background: linear-gradient(45deg, var(--primary-color), var(--secondary-color)); 
                              color: white; padding: 0.5rem 1rem; border-radius: 20px; text-decoration: none; 
                              font-weight: bold; margin-top: 1rem;">
                        View on Mercari 🔗
                    </a>
                    """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

def get_showcase_products(data_handler: DataHandler, categories) -> List[Dict]:
    """Get products for showcase from specific categories"""
    if isinstance(categories, str):
        categories = [categories]
    
    all_products = data_handler.get_all_products()
    showcase_products = []
    
    for product in all_products:
        if product.get('category') in categories:
            showcase_products.append(product)
    
    # Sort by rating and return top products
    showcase_products.sort(key=lambda x: x.get('seller_rating', 0), reverse=True)
    return showcase_products[:6]  # Limit to 6 products per category

def display_showcase_grid(products: List[Dict]):
    """Display products in a grid layout"""
    if not products:
        st.info("No products available in this category.")
        return
    
    # Create a grid layout with 3 columns
    cols = st.columns(3)
    
    for i, product in enumerate(products):
        with cols[i % 3]:
            st.markdown(f"""
            <div class="product-card" style="animation: fadeInScale {0.5 + i*0.1}s ease-out; height: 400px;">
                <img src="{product.get('image_url', 'https://via.placeholder.com/150')}" 
                     class="product-image" 
                     style="width: 100%; height: 150px; object-fit: cover; margin-bottom: 1rem;">
                
                <h4 style="color: var(--text-color); margin-bottom: 0.5rem; height: 60px; overflow: hidden;">
                    {product['name'][:50]}{'...' if len(product['name']) > 50 else ''}
                </h4>
                
                <span class="category-pill">{product['category']}</span>
                
                <div class="price-tag" style="margin: 1rem 0; font-size: 1.3rem;">
                    ¥{product['price']:,}
                </div>
                
                <div style="margin: 0.5rem 0;">
                    <span class="star-rating">{'⭐' * int(product['seller_rating'])}</span> 
                    <strong>({product['seller_rating']}/5)</strong>
                </div>
                
                <div style="margin-top: 1rem;">
                    <strong>Condition:</strong> {product['condition'].title()}
                </div>
            </div>
            """, unsafe_allow_html=True)

def display_product_showcase(data_handler: DataHandler):
    """Display popular products showcase section"""
    st.markdown("""
    <div class="product-showcase">
    <h2 class="section-header" style="font-size: 2rem; margin-bottom: 1.5rem;">
        🔥 Popular Items on Mercari Japan
    </h2>
    """, unsafe_allow_html=True)
    
    # Category tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎮 Electronics", "👗 Fashion", "🎯 Entertainment", "🏠 Home & Beauty"])
    
    with tab1:
        electronics_products = get_showcase_products(data_handler, "Electronics")
        display_showcase_grid(electronics_products)
    
    with tab2:
        fashion_products = get_showcase_products(data_handler, "Fashion")
        display_showcase_grid(fashion_products)
    
    with tab3:
        entertainment_products = get_showcase_products(data_handler, ["Trading Cards", "Gaming", "Collectibles"])
        display_showcase_grid(entertainment_products)
    
    with tab4:
        home_products = get_showcase_products(data_handler, ["Watches", "Home & Kitchen"])
        display_showcase_grid(home_products)
    
    st.markdown("</div>", unsafe_allow_html=True)

# Main application
def main():
    # Enhanced header with animation
    st.markdown("""
    <div class="section-header">
        🛍️ Mercari Japan Shopping Assistant
    </div>
    <div style="text-align: center; margin-bottom: 2rem; font-size: 1.2rem; color: #666;">
        Ask me about products you want to buy on Mercari Japan in English or Japanese!
    </div>
    """, unsafe_allow_html=True)
    
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
    
    # Product Showcase Section
    display_product_showcase(data_handler)



if __name__ == "__main__":
    main()
