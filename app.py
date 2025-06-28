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

# Dark blue theme CSS with excellent contrast
st.markdown("""
<style>
    .main {
        padding: 2rem;
        background-color: #0f172a;
        color: #f1f5f9;
    }
    
    /* Main title styling */
    h1 {
        color: #f1f5f9 !important;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        font-size: 2.5rem;
        font-weight: 700;
    }
    
    /* Subtitle styling */
    .main > div > div > div > div > p {
        color: #cbd5e1 !important;
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    .product-card {
        background: linear-gradient(145deg, #1e293b, #334155);
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        border: 1px solid #475569;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .product-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8, #60a5fa);
    }
    
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(96, 165, 250, 0.25);
        border-color: #60a5fa;
    }
    
    .product-card h3, .product-card h4 {
        color: #f1f5f9 !important;
        margin-bottom: 1rem;
        font-weight: 600;
        line-height: 1.3;
    }
    
    .product-image {
        border-radius: 12px;
        max-width: 100%;
        height: auto;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }
    
    .price-tag {
        color: #fbbf24;
        font-size: 1.4rem;
        font-weight: 700;
        margin: 0.5rem 0;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        background: linear-gradient(45deg, #fbbf24, #f59e0b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .category-badge {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8);
        color: white;
        padding: 0.4rem 1.2rem;
        border-radius: 25px;
        font-size: 0.85rem;
        display: inline-block;
        margin: 0.3rem 0;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .section-title {
        text-align: center;
        color: #f1f5f9 !important;
        margin: 2rem 0 1rem 0;
        font-size: 2.2rem;
        font-weight: 700;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #f1f5f9, #cbd5e1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .star-rating {
        color: #fbbf24;
        font-size: 1.1rem;
        text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Tab styling for dark theme */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #1e293b;
        padding: 0.8rem;
        border-radius: 12px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        border: 1px solid #334155;
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 12px 24px;
        background-color: #334155;
        border-radius: 10px;
        border: 1px solid #475569;
        color: #cbd5e1 !important;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8) !important;
        color: white !important;
        border-color: #3b82f6;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
        transform: translateY(-1px);
    }
    
    /* Chat message styling */
    .stChatMessage {
        background: linear-gradient(145deg, #1e293b, #334155);
        border: 1px solid #475569;
        border-radius: 12px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        color: #f1f5f9;
        box-shadow: 0 4px 16px rgba(0,0,0,0.2);
    }
    
    /* Product text content contrast */
    .product-card p, .product-card div {
        color: #cbd5e1 !important;
        line-height: 1.6;
    }
    
    /* Improve markdown text visibility */
    .markdown-text-container {
        color: #f1f5f9 !important;
    }
    
    /* Chat input styling */
    .stChatInput > div > div > textarea {
        background-color: #1e293b !important;
        border: 2px solid #475569 !important;
        border-radius: 12px !important;
        color: #f1f5f9 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
    }
    
    .stChatInput > div > div > textarea:focus {
        border-color: #60a5fa !important;
        box-shadow: 0 0 0 3px rgba(96, 165, 250, 0.2) !important;
    }
    
    /* Divider styling */
    hr {
        border: none;
        height: 2px;
        background: linear-gradient(90deg, #3b82f6, #1d4ed8, #60a5fa);
        margin: 2rem 0;
        border-radius: 1px;
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #3b82f6, #1d4ed8);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.8rem 2rem;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(59, 130, 246, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #1e293b;
    }
    
    /* Responsive grid adjustments */
    @media (max-width: 768px) {
        .product-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        .section-title {
            font-size: 1.8rem;
        }
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_services():
    """Initialize all services with proper error handling"""
    try:
        # Initialize LLM service with mock mode for stability
        llm_service = LLMService(mock_mode=True)
        
        # Initialize data handler
        data_handler = DataHandler()
        
        # Initialize product ranker
        product_ranker = ProductRanker()
        
        # Initialize translator
        translator = Translator(llm_service)
        
        return llm_service, data_handler, product_ranker, translator
    except Exception as e:
        st.error(f"Error initializing services: {e}")
        return None, None, None, None

def display_product_card(product: Dict, index: Optional[int] = None):
    """Display a single product card with enhanced styling"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if product.get('image_url'):
            st.image(product['image_url'], use_container_width=True, caption="Product Image")
        else:
            st.image("https://via.placeholder.com/200x200?text=No+Image", use_container_width=True, caption="No Image Available")
    
    with col2:
        st.markdown(f"""
        <div class="product-card">
            <h3>{product['name']}</h3>
            <div class="price-tag">¥{product['price']:,}</div>
            <div class="category-badge">{product.get('category', 'Unknown')}</div>
            <p><strong>Condition:</strong> {product['condition']}</p>
            <p><strong>Seller Rating:</strong> <span class="star-rating">{'⭐' * int(product['seller_rating'])}</span> ({product['seller_rating']}/5)</p>
            {f'<p><strong>Brand:</strong> {product["brand"]}</p>' if product.get('brand') else ''}
            {f'<p><strong>Description:</strong> {product["description"]}</p>' if product.get('description') else ''}
        </div>
        """, unsafe_allow_html=True)

def display_products(products: List[Dict]):
    """Display a list of products in a grid layout"""
    if not products:
        st.warning("No products found matching your criteria.")
        return
    
    for i, product in enumerate(products):
        display_product_card(product, i)

def get_showcase_products(data_handler: DataHandler, categories) -> List[Dict]:
    """Get showcase products for different categories"""
    showcase_products = {}
    
    for category in categories:
        try:
            products = data_handler.get_products_by_category(category)
            if products:
                showcase_products[category] = products[:4]  # Top 4 products per category
            else:
                # If no products found, try to get any products and show them
                all_products = data_handler.get_all_products()
                showcase_products[category] = all_products[:4]  # Show any products as fallback
        except Exception as e:
            st.error(f"Error fetching {category} products: {e}")
            showcase_products[category] = []
    
    return showcase_products

def display_showcase_grid(products: List[Dict]):
    """Display products in a responsive grid layout"""
    if not products:
        st.info("No products available in this category. Showing sample products instead.")
        # Show some sample products as fallback
        sample_products = [
            {
                "id": "sample1",
                "name": "Sample Product 1",
                "price": 10000,
                "condition": "new",
                "seller_rating": 4.5,
                "category": "Sample"
            },
            {
                "id": "sample2", 
                "name": "Sample Product 2",
                "price": 15000,
                "condition": "like_new",
                "seller_rating": 4.8,
                "category": "Sample"
            }
        ]
        products = sample_products
    
    # Calculate number of columns based on screen size
    cols = st.columns(min(4, len(products)))
    
    for i, product in enumerate(products):
        with cols[i % len(cols)]:
            _display_product_card_compact(product)

def _display_product_card_compact(product: Dict):
    """Display a compact product card for grid layout"""
    st.markdown(f"""
    <div class="product-card" style="margin: 0.5rem 0;">
        <h4>{product['name'][:50]}{'...' if len(product['name']) > 50 else ''}</h4>
        <div class="price-tag">¥{product['price']:,}</div>
        <div class="category-badge">{product.get('category', 'Unknown')}</div>
        <p><strong>Condition:</strong> {product['condition']}</p>
        <p><strong>Rating:</strong> <span class="star-rating">{'⭐' * int(product['seller_rating'])}</span></p>
    </div>
    """, unsafe_allow_html=True)

def display_product_showcase(data_handler: DataHandler):
    """Display product showcase with category tabs"""
    st.markdown('<h2 class="section-title">🛍️ Product Showcase</h2>', unsafe_allow_html=True)
    
    categories = ["Electronics", "Fashion", "Entertainment", "Home & Beauty"]
    tab1, tab2, tab3, tab4 = st.tabs([f"📱 {categories[0]}", f"👗 {categories[1]}", f"🎮 {categories[2]}", f"🏠 {categories[3]}"])
    
    showcase_products = get_showcase_products(data_handler, categories)
    
    with tab1:
        display_showcase_grid(showcase_products.get("Electronics", []))
    
    with tab2:
        display_showcase_grid(showcase_products.get("Fashion", []))
    
    with tab3:
        display_showcase_grid(showcase_products.get("Entertainment", []))
    
    with tab4:
        display_showcase_grid(showcase_products.get("Home & Beauty", []))

def main():
    """Main application function"""
    try:
        # Initialize services
        llm_service, data_handler, product_ranker, translator = initialize_services()
        
        if not all([llm_service, data_handler, product_ranker, translator]):
            st.error("Failed to initialize services. Please check your configuration.")
            return
        
        # Main title
        st.markdown('<h1>🛍️ Mercari Japan AI Shopping Assistant</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; color: #cbd5e1; font-size: 1.2rem;">Your intelligent shopping companion for Mercari Japan</p>', unsafe_allow_html=True)
        
        # Sidebar configuration
        with st.sidebar:
            st.markdown("### ⚙️ Settings")
            
            # Language selection
            language = st.selectbox(
                "🌐 Language",
                ["English", "Japanese"],
                index=0
            )
            
            # Real-time scraping toggle
            use_real_time = st.checkbox(
                "🔄 Real-time Scraping",
                value=False,
                help="Enable real-time scraping from Mercari Japan (may be slower)"
            )
            
            st.markdown("---")
            st.markdown("### 📊 Statistics")
            try:
                all_products = data_handler.get_all_products()
                st.metric("Total Products", len(all_products))
            except Exception as e:
                st.error(f"Error loading statistics: {e}")
        
        # Main content area
        tab1, tab2 = st.tabs(["💬 Chat Assistant", "🛍️ Browse Products"])
        
        with tab1:
            st.markdown('<h2 class="section-title">💬 AI Shopping Assistant</h2>', unsafe_allow_html=True)
            
            # Initialize chat history
            if "messages" not in st.session_state:
                st.session_state.messages = []
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            # Chat input
            if prompt := st.chat_input("Tell me what you're looking for..."):
                # Add user message to chat history
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                
                # Process the query
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Searching for products..."):
                        try:
                            # Detect language
                            detected_lang = "ja" if language == "Japanese" else "en"
                            
                            # Parse query
                            query_filters = llm_service.parse_query(prompt, detected_lang)
                            
                            # Search products
                            if use_real_time:
                                products = data_handler.search_mercari_real_time(prompt, query_filters)
                            else:
                                products = data_handler.search_products(prompt, query_filters)
                            
                            # Rank products
                            if products:
                                ranked_products = product_ranker.rank_products(products, query_filters)
                                top_products = ranked_products[:3]  # Top 3 recommendations
                                
                                # Generate recommendations
                                recommendations = llm_service.generate_recommendations(prompt, top_products, detected_lang)
                                
                                # Display recommendations
                                st.markdown(recommendations)
                                
                                # Display top products
                                st.markdown("### 🎯 Top Recommendations")
                                display_products(top_products)
                            else:
                                st.warning("No products found matching your criteria. Please try a different search.")
                            
                        except Exception as e:
                            st.error(f"Error processing your request: {e}")
                            st.info("Please try again or check your internet connection.")
                
                # Add assistant response to chat history
                st.session_state.messages.append({"role": "assistant", "content": "I found some products for you! Check the recommendations above."})
        
        with tab2:
            display_product_showcase(data_handler)
    
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please refresh the page and try again.")

if __name__ == "__main__":
    main()