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

# Clean, modern CSS
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    
    .product-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .product-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .product-image {
        border-radius: 8px;
        max-width: 100%;
        height: auto;
    }
    
    .price-tag {
        color: #ff4444;
        font-size: 1.3rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .category-badge {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        display: inline-block;
        margin: 0.3rem 0;
        font-weight: bold;
    }
    
    .section-title {
        text-align: center;
        color: #333;
        margin: 2rem 0 1rem 0;
        font-size: 2rem;
        background: linear-gradient(45deg, #667eea, #764ba2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .star-rating {
        color: #ffd700;
        font-size: 1.1rem;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        background-color: #f8f9fa;
        border-radius: 10px;
        border: 1px solid #e9ecef;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
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

def display_product_card(product: Dict, index: Optional[int] = None):
    """Display a single product in a clean card format"""
    st.markdown('<div class="product-card">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if product.get("image_url"):
            st.image(product["image_url"], width=150)
    
    with col2:
        if index:
            st.subheader(f"{index}. {product['name']}")
        else:
            st.subheader(product['name'])
        
        st.markdown(f'<div class="category-badge">{product["category"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="price-tag">¥{product["price"]:,}</div>', unsafe_allow_html=True)
        
        st.markdown(f"""
        **Condition:** {product['condition'].title()}  
        **Seller Rating:** <span class="star-rating">{'⭐' * int(product['seller_rating'])}</span> ({product['seller_rating']}/5)
        """, unsafe_allow_html=True)
        
        if product.get('url'):
            st.markdown(f"[🔗 View on Mercari]({product['url']})")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_products(products: List[Dict]):
    """Display product recommendations"""
    if not products:
        st.info("No products found matching your criteria.")
        return
    
    for i, product in enumerate(products, 1):
        display_product_card(product, i)

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
    """Display products in a clean grid layout"""
    if not products:
        st.info("No products available in this category.")
        return
    
    # Create a grid layout with 3 columns
    cols = st.columns(3)
    
    for i, product in enumerate(products):
        with cols[i % 3]:
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            if product.get("image_url"):
                st.image(product["image_url"], use_container_width=True)
            
            st.markdown(f"**{product['name'][:40]}{'...' if len(product['name']) > 40 else ''}**")
            st.markdown(f'<div class="category-badge">{product["category"]}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="price-tag">¥{product["price"]:,}</div>', unsafe_allow_html=True)
            st.markdown(f"**Rating:** <span class='star-rating'>{'⭐' * int(product['seller_rating'])}</span> ({product['seller_rating']}/5)", unsafe_allow_html=True)
            st.markdown(f"**Condition:** {product['condition'].title()}")
            
            st.markdown('</div>', unsafe_allow_html=True)

def display_product_showcase(data_handler: DataHandler):
    """Display popular products showcase section"""
    st.markdown('<h2 class="section-title">🔥 Popular Items on Mercari Japan</h2>', unsafe_allow_html=True)
    
    # Category tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📱 Electronics", "👗 Fashion", "🎮 Entertainment", "🏠 Home & Beauty"])
    
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
    
    # Product Showcase Section
    st.markdown("---")
    display_product_showcase(data_handler)

if __name__ == "__main__":
    main()