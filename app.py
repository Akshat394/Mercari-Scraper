from dotenv import load_dotenv
load_dotenv()
import streamlit as st
import os
import json
from typing import Dict, List, Optional
from core.llm_service import LLMService
from core.data_handler import DataHandler
from core.product_ranker import ProductRanker
from core.translator import Translator
from utils.helpers import detect_language, format_product_display
import uuid
from collections import defaultdict
from datetime import datetime
from core.chat_assistant import ChatAssistant
from core.chat_scraper import ChatScraperSync

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

def feedback_button(product_id, session_id, db_manager, action_type, icon, tooltip):
    """Create a feedback button for a product"""
    is_feedback = db_manager.is_product_feedback(session_id, product_id, action_type)
    button_text = f"{icon} {action_type.title()}"
    if st.button(button_text, key=f"{action_type}_{product_id}", help=tooltip):
        db_manager.save_user_feedback(session_id, product_id, action_type)
        st.success(f"Product {action_type}!")
        st.rerun()

def display_cart_sidebar(session_id, db_manager):
    """Display cart contents in the sidebar"""
    st.markdown("### 🛒 Your Cart")
    
    cart_items = db_manager.get_cart_items(session_id)
    cart_total = db_manager.get_cart_total(session_id)
    
    if not cart_items:
        st.info("Your cart is empty.")
        return
    
    # Display cart items
    for item in cart_items:
        with st.container(border=True):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if item.get('image_url'):
                    st.image(item['image_url'], width=60, caption="")
                else:
                    st.image("https://via.placeholder.com/60x60?text=No+Image", width=60, caption="")
            
            with col2:
                st.markdown(f"**{item['product_title'][:30]}{'...' if len(item['product_title']) > 30 else ''}**")
                st.markdown(f"¥{item['price']:,}")
                st.markdown(f"*{item.get('condition', 'N/A')}*")
                
                if st.button("🗑️ Remove", key=f"remove_cart_{item['product_id']}", help="Remove from cart"):
                    db_manager.remove_from_cart(item['product_id'], session_id)
                    st.success("Removed from cart!")
                    st.rerun()
    
    # Cart total and actions
    st.markdown("---")
    st.markdown(f"**Total: ¥{cart_total:,}**")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Cart", type="secondary"):
            db_manager.clear_cart(session_id)
            st.success("Cart cleared!")
            st.rerun()
    
    with col2:
        if st.button("💳 Checkout", type="primary"):
            st.info("Checkout functionality coming soon!")

def display_product_card(product: Dict, index: Optional[int] = None, session_id: str = None, db_manager=None):
    """Display a single product card with enhanced styling"""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if product.get('image_url'):
            st.image(product['image_url'], use_container_width=True, caption="Product Image")
        else:
            st.image("https://via.placeholder.com/200x200?text=No+Image", use_container_width=True, caption="No Image Available")
        
        # Cart button
        if session_id and db_manager:
            is_in_cart = db_manager.is_in_cart(product['id'], session_id)
            
            if is_in_cart:
                if st.button("✅ Added to Cart", key=f"cart_{product['id']}", disabled=True):
                    pass  # Button is disabled when already in cart
            else:
                if st.button("🛒 Add to Cart", key=f"cart_{product['id']}"):
                    result = db_manager.add_to_cart(product, session_id)
                    if result == "Added to cart":
                        st.success("✅ Added to cart!")
                    else:
                        st.info(result)
                    st.rerun()
        
        # Feedback buttons
        if session_id and db_manager:
            feedback_button(product['id'], session_id, db_manager, 'liked', '❤️', 'Like this product')
            feedback_button(product['id'], session_id, db_manager, 'saved', '⭐', 'Save this product')
            feedback_button(product['id'], session_id, db_manager, 'dismissed', '🚫', 'Dismiss this product')
    
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

def display_products(products: List[Dict], session_id: str = None, db_manager=None):
    """Display a list of products in a grid layout"""
    if not products:
        st.warning("No products found matching your criteria.")
        return
    
    for i, product in enumerate(products):
        display_product_card(product, i, session_id=session_id, db_manager=db_manager)

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

def display_showcase_grid(products: List[Dict], session_id: str = None, db_manager=None):
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
            _display_product_card_compact(product, session_id=session_id, db_manager=db_manager)

def _display_product_card_compact(product: Dict, session_id: str = None, db_manager=None):
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
    
    # Add cart button for compact cards
    if session_id and db_manager:
        is_in_cart = db_manager.is_in_cart(product['id'], session_id)
        
        if is_in_cart:
            st.button("✅ Added", key=f"compact_cart_{product['id']}", disabled=True)
        else:
            if st.button("🛒 Add to Cart", key=f"compact_cart_{product['id']}"):
                result = db_manager.add_to_cart(product, session_id)
                if result == "Added to cart":
                    st.success("✅ Added to cart!")
                else:
                    st.info(result)
                st.rerun()

def display_product_showcase(data_handler: DataHandler):
    """Display product showcase with category tabs"""
    st.markdown('<h2 class="section-title">🛍️ Product Showcase</h2>', unsafe_allow_html=True)
    
    categories = ["Electronics", "Fashion", "Entertainment", "Home & Beauty"]
    tab1, tab2, tab3, tab4 = st.tabs([f"📱 {categories[0]}", f"👗 {categories[1]}", f"🎮 {categories[2]}", f"🏠 {categories[3]}"])
    
    showcase_products = get_showcase_products(data_handler, categories)
    
    with tab1:
        display_showcase_grid(showcase_products.get("Electronics", []), session_id=st.session_state.session_id, db_manager=data_handler.db_manager)
    
    with tab2:
        display_showcase_grid(showcase_products.get("Fashion", []), session_id=st.session_state.session_id, db_manager=data_handler.db_manager)
    
    with tab3:
        display_showcase_grid(showcase_products.get("Entertainment", []), session_id=st.session_state.session_id, db_manager=data_handler.db_manager)
    
    with tab4:
        display_showcase_grid(showcase_products.get("Home & Beauty", []), session_id=st.session_state.session_id, db_manager=data_handler.db_manager)

def get_available_brands(data_handler, category):
    """Fetch unique brands for a given category from the database."""
    products = data_handler.get_products_by_category(category)
    brands = set()
    for p in products:
        if p.get('brand') and p['brand'].strip():
            brands.add(p['brand'])
    return sorted(list(brands))

def get_price_range(products):
    if not products:
        return (0, 100000)
    prices = [p['price'] for p in products if p.get('price') is not None]
    if not prices:
        return (0, 100000)
    return (min(prices), max(prices))

def _brand_matches(product_brand: str, filter_brands) -> bool:
    """Check if product brand matches any of the filter brands"""
    if not product_brand or not filter_brands:
        return True
    
    product_brand_lower = product_brand.lower()
    
    # Handle filter_brands as either string or list
    if isinstance(filter_brands, list):
        return any(brand.lower() == product_brand_lower for brand in filter_brands if brand)
    else:
        return filter_brands.lower() == product_brand_lower

def sidebar_filters(data_handler):
    st.markdown('### 🗂️ Category & Filters')
    categories = ["Electronics", "Fashion", "Home Appliances", "Toys", "Books"]
    category = st.selectbox("Select Category", categories, key="category_select")
    
    # Clear cache when category changes
    if "last_category" not in st.session_state:
        st.session_state.last_category = category
    elif st.session_state.last_category != category:
        # Category changed, clear all filter caches
        for key in list(st.session_state.keys()):
            if key.startswith("filter_cache_"):
                del st.session_state[key]
        st.session_state.last_category = category
    
    # Use session state to cache filter data and prevent repeated database calls
    cache_key = f"filter_cache_{category}"
    if cache_key not in st.session_state:
        # Fetch products for this category to get filter options (only once per category change)
        products = data_handler.get_products_by_category(category)
        price_min, price_max = get_price_range(products)
        brands = get_available_brands(data_handler, category)
        
        st.session_state[cache_key] = {
            "price_min": price_min,
            "price_max": price_max,
            "brands": brands
        }
    else:
        # Use cached values
        cached_data = st.session_state[cache_key]
        price_min = cached_data["price_min"]
        price_max = cached_data["price_max"]
        brands = cached_data["brands"]
    
    # Price Range
    price_range = st.slider(
        "Price Range (¥)",
        min_value=price_min,
        max_value=price_max if price_max > price_min else price_min+10000,
        value=(price_min, price_max if price_max > price_min else price_min+10000),
        step=500,
        key="price_slider"
    )
    
    # Condition
    condition_options = ["new", "like_new", "used", "very_good", "good", "acceptable"]
    condition = st.selectbox("Condition", condition_options, index=0, key="condition_select")
    
    # Brand
    brand_selected = st.multiselect("Brand", brands, key="brand_multiselect")
    
    # Seller Rating
    seller_rating = st.slider("Minimum Seller Rating", min_value=0.0, max_value=5.0, value=0.0, step=0.1, key="seller_rating_slider")
    
    # Shipping Included (optional, if data available)
    shipping_included = st.checkbox("Shipping Included", value=False, key="shipping_checkbox")
    
    # Build filter dict
    filters = {
        "category": category,
        "price_range": {"min": price_range[0], "max": price_range[1]},
        "condition": condition,
        "brand": brand_selected,
        "seller_rating": seller_rating,
        "shipping_included": shipping_included
    }
    return filters

def main():
    """Main application function"""
    try:
        # Initialize services
        llm_service, data_handler, product_ranker, translator = initialize_services()
        chat_assistant = ChatAssistant(mock_mode=False)  # Use real OpenAI API
        chat_scraper = ChatScraperSync()
        
        if not all([llm_service, data_handler, product_ranker, translator]):
            st.error("Failed to initialize services. Please check your configuration.")
            return
        
        # Initialize session state for user session ID
        if "session_id" not in st.session_state:
            st.session_state.session_id = str(uuid.uuid4())
        
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
                value=True,  # Enable by default
                help="Enable real-time scraping from Mercari Japan (recommended)"
            )
            
            if use_real_time:
                st.success("✅ Real-time scraping enabled - fetching live data from Mercari Japan")
            else:
                st.info("ℹ️ Using cached database data for faster performance")
            
            st.markdown("---")
            
            # Category & Filters
            filters = sidebar_filters(data_handler)
            st.markdown("---")
            
            # Search History Section
            st.markdown("### 📚 Search History")
            
            try:
                # Get search summary
                search_summary = data_handler.get_search_summary(st.session_state.session_id)
                
                # Display summary metrics
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Searches", search_summary.get("total_searches", 0))
                with col2:
                    st.metric("Recent (24h)", search_summary.get("recent_searches", 0))
                
                # Display common queries
                common_queries = search_summary.get("common_queries", [])
                if common_queries:
                    st.markdown("**Popular Queries:**")
                    for query_info in common_queries[:3]:  # Top 3
                        st.markdown(f"• {query_info['query']} ({query_info['count']})")
                
                # Show recent search history
                recent_history = data_handler.get_search_history(st.session_state.session_id, limit=10)
                if recent_history:
                    st.markdown("**Recent Searches:**")
                    for entry in recent_history[:5]:  # Show last 5
                        # Create a clickable button for each search
                        if st.button(
                            f"🔍 {entry['query_text'][:30]}{'...' if len(entry['query_text']) > 30 else ''}",
                            key=f"history_{entry['id']}",
                            help=f"Search: {entry['query_text']}\nFound: {entry['product_title']}\nPrice: ¥{entry['price']:,}"
                        ):
                            # Store the query to be used in the main search
                            st.session_state.replay_query = entry['query_text']
                            st.rerun()
                
                # Clear history button
                if st.button("🗑️ Clear History", type="secondary"):
                    data_handler.clear_search_history(st.session_state.session_id)
                    st.success("Search history cleared!")
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error loading search history: {e}")
            
            st.markdown("---")
            st.markdown("### 📊 Statistics")
            try:
                # Cache the total products count to prevent repeated database calls
                if "total_products_count" not in st.session_state:
                    all_products = data_handler.get_all_products()
                    st.session_state.total_products_count = len(all_products)
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.metric("Total Products", st.session_state.total_products_count)
                with col2:
                    if st.button("🔄", help="Refresh statistics", key="refresh_stats"):
                        all_products = data_handler.get_all_products()
                        st.session_state.total_products_count = len(all_products)
                        st.rerun()
            except Exception as e:
                st.error(f"Error loading statistics: {e}")
            
            # Saved/Liked Items
            st.markdown("---")
            st.markdown("### ⭐ Saved Items")
            saved_items = data_handler.db_manager.get_user_feedback(st.session_state.session_id, action_type="saved")
            if saved_items:
                for item in saved_items[:5]:
                    st.markdown(f"- {item['product_id']} <span style='color:#fbbf24'>⭐</span>", unsafe_allow_html=True)
            else:
                st.caption("No saved items yet.")
            st.markdown("### ❤️ Liked Items")
            liked_items = data_handler.db_manager.get_user_feedback(st.session_state.session_id, action_type="liked")
            if liked_items:
                for item in liked_items[:5]:
                    st.markdown(f"- {item['product_id']} <span style='color:#f87171'>❤️</span>", unsafe_allow_html=True)
            else:
                st.caption("No liked items yet.")
            
            # Cart Section
            st.markdown("---")
            display_cart_sidebar(st.session_state.session_id, data_handler.db_manager)
        
        # Main content area
        tab1, tab2 = st.tabs(["💬 Chat Assistant", "🛍️ Browse Products"])
        
        with tab1:
            st.markdown('<h2 class="section-title">💬 AI Shopping Assistant</h2>', unsafe_allow_html=True)
            # Only show chat interface, no filters
            if "chat_messages" not in st.session_state:
                st.session_state.chat_messages = []
            # Display chat history
            for message in st.session_state.chat_messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            # Chat input
            if prompt := st.chat_input("What are you looking for? (e.g. cheap Nintendo Switch, blue women's bag)"):
                st.session_state.chat_messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)
                with st.chat_message("assistant"):
                    with st.spinner("🔍 Searching for products..."):
                        try:
                            # 1. LLM: parse query, extract keywords, translate
                            parsed_query = chat_assistant.parse_natural_language_query(prompt, language="en")
                            # 2. Build filters for scraping
                            filters = chat_assistant.extract_search_filters(parsed_query)
                            # 3. Use Japanese keywords for search
                            search_keyword = " ".join(parsed_query.get("japanese_keywords", []))
                            # 4. Real-time scrape (no cache)
                            products = chat_scraper.search_products_fast(search_keyword, filters, max_results=5)
                            # 5. Show only 3-5 most relevant
                            products = products[:5]
                            # 6. LLM: generate reasoning
                            reasoning = chat_assistant.generate_search_reasoning(prompt, parsed_query, products)
                            st.markdown(reasoning)
                            st.markdown("### 🎯 Top Results")
                            if products:
                                for idx, product in enumerate(products):
                                    with st.container():
                                        st.image(product["image_url"], width=180)
                                        st.markdown(f"**{product['name']}**")
                                        st.markdown(f"<span class='price-tag'>¥{product['price']:,}</span>", unsafe_allow_html=True)
                                        st.markdown(f"Condition: {product['condition'].capitalize()}")
                                        st.markdown(f"Seller Rating: {product.get('seller_rating', 'N/A')}")
                                        st.markdown(f"[View on Mercari]({product['product_url']})", unsafe_allow_html=True)
                                        if st.button("Add to Cart", key=f"add_cart_{idx}"):
                                            data_handler.db_manager.add_to_cart(st.session_state.session_id, product)
                                            st.success("Added to cart!")
                            else:
                                st.warning("No products found. Try a different query.")
                        except Exception as e:
                            st.error(f"Error: {e}")
                            st.info("Please try again or check your internet connection.")
                st.session_state.chat_messages.append({"role": "assistant", "content": "See the results above!"})
        
        with tab2:
            # Use the same filters for browsing
            browse_products = data_handler.get_products_by_category(filters['category'])
            # Apply backend filtering
            browse_products = [
                p for p in browse_products
                if filters['price_range']['min'] <= p.get('price', 0) <= filters['price_range']['max']
                and (filters['condition'] == p.get('condition', '').lower() or filters['condition'] == 'all')
                and (not filters['brand'] or _brand_matches(p.get('brand', ''), filters['brand']))
                and p.get('seller_rating', 0) >= filters['seller_rating']
                and (not filters['shipping_included'] or p.get('shipping_included', True))
            ]
            display_product_showcase(data_handler)
            display_products(browse_products, session_id=st.session_state.session_id, db_manager=data_handler.db_manager)
    
    except Exception as e:
        st.error(f"Application error: {e}")
        st.info("Please refresh the page and try again.")
    finally:
        pass

if __name__ == "__main__":
    main()