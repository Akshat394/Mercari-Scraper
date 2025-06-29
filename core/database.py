import os
import json
import re
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean, DateTime, ARRAY, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
from core.sample_data import SAMPLE_MERCARI_DATA

Base = declarative_base()

class Product(Base):
    """SQLAlchemy model for Mercari products"""
    __tablename__ = "products"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    condition = Column(String, nullable=False)
    seller_rating = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    brand = Column(String)
    image_url = Column(String)
    url = Column(String)
    description = Column(Text)

class SearchHistory(Base):
    """SQLAlchemy model for storing Mercari search results"""
    __tablename__ = "search_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_text = Column(String, nullable=False)
    product_title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image_url = Column(String)
    condition = Column(String)
    seller_rating = Column(Float)
    tags = Column(ARRAY(String))  # PostgreSQL array for tags
    created_at = Column(DateTime, default=datetime.utcnow)
    session_id = Column(String)  # To group searches by user session
    product_id = Column(String)  # Original Mercari product ID
    category = Column(String)
    brand = Column(String)
    url = Column(String)
    description = Column(Text)

class UserFeedback(Base):
    """SQLAlchemy model for user feedback on products"""
    __tablename__ = "user_feedback"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)  # Removed ForeignKey constraint
    action_type = Column(String, nullable=False)  # liked, dismissed, saved, etc.
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class CartItem(Base):
    """SQLAlchemy model for cart items"""
    __tablename__ = "cart_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, nullable=False)
    product_id = Column(String, nullable=False)
    product_title = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    image_url = Column(String)
    condition = Column(String)
    category = Column(String)
    brand = Column(String)
    url = Column(String)
    added_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Manages database connections and operations for Mercari products and search history"""
    
    def __init__(self, connection_string=None):
        # Use the provided PostgreSQL connection string or default
        self.database_url = connection_string or "postgresql://database_owner:npg_EQSL90iRFWVp@ep-spring-morning-a8c42kzl-pooler.eastus2.azure.neon.tech/database?sslmode=require&channel_binding=require"
        
        # Create engine with connection pooling for better performance
        self.engine = create_engine(
            self.database_url,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=300
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.create_tables()
        
        # Initialize with sample data if empty
        self._initialize_sample_data()
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text to remove null bytes and other problematic characters"""
        if not text:
            return ""
        
        # Remove null bytes and other control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text))
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _sanitize_product_data(self, product_data: Dict) -> Dict:
        """Sanitize all text fields in product data"""
        sanitized = {}
        for key, value in product_data.items():
            if isinstance(value, str):
                sanitized[key] = self._sanitize_text(value)
            else:
                sanitized[key] = value
        return sanitized
    
    def _initialize_sample_data(self):
        """Initialize database with sample data if it's empty"""
        session = self.get_session()
        try:
            # Check if data already exists
            existing_count = session.query(Product).count()
            if existing_count > 0:
                print(f"Database already contains {existing_count} products")
                return
            
            # Add sample data
            for product_data in SAMPLE_MERCARI_DATA:
                # Sanitize the data
                sanitized_data = self._sanitize_product_data(product_data)
                
                product = Product(
                    id=sanitized_data["id"],
                    name=sanitized_data["name"],
                    price=sanitized_data["price"],
                    condition=sanitized_data["condition"],
                    seller_rating=sanitized_data["seller_rating"],
                    category=sanitized_data["category"],
                    brand=sanitized_data.get("brand"),
                    image_url=sanitized_data.get("image_url"),
                    url=sanitized_data.get("url"),
                    description=sanitized_data.get("description")
                )
                session.add(product)
            
            session.commit()
            print(f"Initialized database with {len(SAMPLE_MERCARI_DATA)} products")
            
        except Exception as e:
            session.rollback()
            print(f"Error initializing sample data: {e}")
        finally:
            session.close()
    
    def store_search_results(self, query_text: str, products: List[Dict], session_id: str = None) -> List[str]:
        """
        Store search results in the search history table
        
        Args:
            query_text: The user's search query
            products: List of product dictionaries
            session_id: Optional session ID to group searches
            
        Returns:
            List of stored search history IDs
        """
        session = self.get_session()
        stored_ids = []
        
        try:
            for product in products:
                # Extract tags from product data
                tags = self._extract_tags_from_product(product)
                
                # Create search history entry
                search_entry = SearchHistory(
                    query_text=self._sanitize_text(query_text),
                    product_title=self._sanitize_text(product.get('name', '')),
                    price=product.get('price', 0),
                    image_url=self._sanitize_text(product.get('image_url', '')),
                    condition=self._sanitize_text(product.get('condition', '')),
                    seller_rating=product.get('seller_rating', 0.0),
                    tags=tags,
                    session_id=session_id,
                    product_id=self._sanitize_text(product.get('id', '')),
                    category=self._sanitize_text(product.get('category', '')),
                    brand=self._sanitize_text(product.get('brand', '')),
                    url=self._sanitize_text(product.get('url', '')),
                    description=self._sanitize_text(product.get('description', ''))
                )
                
                session.add(search_entry)
                stored_ids.append(str(search_entry.id))
            
            session.commit()
            print(f"Stored {len(products)} search results for query: {query_text}")
            return stored_ids
            
        except Exception as e:
            session.rollback()
            print(f"Error storing search results: {e}")
            return []
        finally:
            session.close()
    
    def _extract_tags_from_product(self, product: Dict) -> List[str]:
        """Extract tags from product data for better searchability using TagProcessor"""
        try:
            from core.tag_processor import TagProcessor
            tag_processor = TagProcessor()
            
            # Use the enhanced tag processor
            tags = tag_processor.process_product_tags(product)
            return tags
            
        except ImportError:
            # Fallback to original logic if TagProcessor is not available
            return self._extract_tags_fallback(product)
    
    def _extract_tags_fallback(self, product: Dict) -> List[str]:
        """Fallback tag extraction logic"""
        tags = []
        
        # Add category as tag
        if product.get('category'):
            tags.append(product['category'].lower())
        
        # Add brand as tag (avoid generic affordable terms)
        if product.get('brand'):
            brand = product['brand'].lower()
            # Skip generic affordable terms
            generic_terms = ['brand affordable', 'affordable brand', 'cheap brand', 'budget brand']
            if not any(term in brand for term in generic_terms):
                tags.append(brand)
        
        # Add condition as tag
        if product.get('condition'):
            tags.append(product['condition'].lower())
        
        # Extract keywords from name
        if product.get('name'):
            name_words = product['name'].lower().split()
            # Add common product keywords
            keywords = ['iphone', 'macbook', 'nintendo', 'switch', 'playstation', 'xbox', 'airpods', 'ipad']
            for keyword in keywords:
                if keyword in name_words:
                    tags.append(keyword)
        
        # Add pricing tags based on price
        price = product.get('price', 0)
        if price <= 2000:
            tags.append('very affordable')
        elif price <= 5000:
            tags.append('affordable')
        elif price <= 15000:
            tags.append('mid range')
        else:
            tags.append('premium')
        
        # Remove duplicates and return
        return list(set(tags))
    
    def get_search_history(self, session_id: str = None, limit: int = 50) -> List[Dict]:
        """
        Get search history, optionally filtered by session
        
        Args:
            session_id: Optional session ID to filter results
            limit: Maximum number of results to return
            
        Returns:
            List of search history entries as dictionaries
        """
        session = self.get_session()
        try:
            query = session.query(SearchHistory)
            
            if session_id:
                query = query.filter(SearchHistory.session_id == session_id)
            
            # Order by most recent first
            query = query.order_by(SearchHistory.created_at.desc()).limit(limit)
            
            results = query.all()
            return [self._search_history_to_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting search history: {e}")
            return []
        finally:
            session.close()
    
    def get_search_history_by_query(self, query_text: str, limit: int = 20) -> List[Dict]:
        """
        Get search history for a specific query
        
        Args:
            query_text: The search query to look for
            limit: Maximum number of results to return
            
        Returns:
            List of search history entries as dictionaries
        """
        session = self.get_session()
        try:
            # Use ILIKE for case-insensitive search
            results = session.query(SearchHistory).filter(
                SearchHistory.query_text.ilike(f"%{query_text}%")
            ).order_by(SearchHistory.created_at.desc()).limit(limit).all()
            
            return [self._search_history_to_dict(result) for result in results]
            
        except Exception as e:
            print(f"Error getting search history by query: {e}")
            return []
        finally:
            session.close()
    
    def get_recent_products_for_query(self, query_text: str, limit: int = 10) -> List[Dict]:
        """
        Get recent products for a query (for recommendations)
        
        Args:
            query_text: The search query
            limit: Maximum number of products to return
            
        Returns:
            List of product dictionaries
        """
        session = self.get_session()
        try:
            # Get recent search results for this query
            results = session.query(SearchHistory).filter(
                SearchHistory.query_text.ilike(f"%{query_text}%")
            ).order_by(SearchHistory.created_at.desc()).limit(limit).all()
            
            # Convert to product format
            products = []
            for result in results:
                product = {
                    "id": result.product_id or str(result.id),
                    "name": result.product_title,
                    "price": result.price,
                    "condition": result.condition,
                    "seller_rating": result.seller_rating,
                    "category": result.category,
                    "brand": result.brand,
                    "image_url": result.image_url,
                    "url": result.url,
                    "description": result.description,
                    "tags": result.tags or []
                }
                products.append(product)
            
            return products
            
        except Exception as e:
            print(f"Error getting recent products for query: {e}")
            return []
        finally:
            session.close()
    
    def _search_history_to_dict(self, search_entry: SearchHistory) -> Dict:
        """Convert SearchHistory object to dictionary"""
        return {
            "id": str(search_entry.id),
            "query_text": search_entry.query_text,
            "product_title": search_entry.product_title,
            "price": search_entry.price,
            "image_url": search_entry.image_url,
            "condition": search_entry.condition,
            "seller_rating": search_entry.seller_rating,
            "tags": search_entry.tags or [],
            "created_at": search_entry.created_at.isoformat() if search_entry.created_at else None,
            "session_id": search_entry.session_id,
            "product_id": search_entry.product_id,
            "category": search_entry.category,
            "brand": search_entry.brand,
            "url": search_entry.url,
            "description": search_entry.description
        }
    
    def get_search_summary(self, session_id: str = None) -> Dict:
        """
        Get a summary of search history for the sidebar
        
        Returns:
            Dictionary with search summary statistics
        """
        session = self.get_session()
        try:
            query = session.query(SearchHistory)
            
            if session_id:
                query = query.filter(SearchHistory.session_id == session_id)
            
            # Get unique queries
            unique_queries = session.query(SearchHistory.query_text).distinct().count()
            
            # Get total searches
            total_searches = query.count()
            
            # Get recent searches (last 24 hours)
            from datetime import timedelta
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_searches = query.filter(SearchHistory.created_at >= yesterday).count()
            
            # Get most common queries
            from sqlalchemy import func
            common_queries = session.query(
                SearchHistory.query_text,
                func.count(SearchHistory.id).label('count')
            ).group_by(SearchHistory.query_text).order_by(
                func.count(SearchHistory.id).desc()
            ).limit(5).all()
            
            return {
                "total_searches": total_searches,
                "unique_queries": unique_queries,
                "recent_searches": recent_searches,
                "common_queries": [{"query": q.query_text, "count": q.count} for q in common_queries]
            }
            
        except Exception as e:
            print(f"Error getting search summary: {e}")
            return {
                "total_searches": 0,
                "unique_queries": 0,
                "recent_searches": 0,
                "common_queries": []
            }
        finally:
            session.close()
    
    def clear_search_history(self, session_id: str = None):
        """Clear search history, optionally for a specific session"""
        session = self.get_session()
        try:
            query = session.query(SearchHistory)
            
            if session_id:
                query = query.filter(SearchHistory.session_id == session_id)
            
            deleted_count = query.delete()
            session.commit()
            print(f"Deleted {deleted_count} search history entries")
            
        except Exception as e:
            session.rollback()
            print(f"Error clearing search history: {e}")
        finally:
            session.close()

    def search_products(self, query: str, filters: Dict[str, Any]) -> List[Dict]:
        """
        Search for products in the database based on query and filters
        """
        session = self.get_session()
        try:
            # Start with base query
            db_query = session.query(Product)
            
            # Apply text search filters
            search_terms = self._extract_search_terms(query, filters)
            if search_terms:
                text_conditions = []
                for term in search_terms:
                    if term:  # Skip empty terms
                        text_conditions.append(Product.name.ilike(f"%{term}%"))
                        text_conditions.append(Product.category.ilike(f"%{term}%"))
                        text_conditions.append(Product.brand.ilike(f"%{term}%"))
                
                # Combine with OR
                from sqlalchemy import or_
                if text_conditions:
                    db_query = db_query.filter(or_(*text_conditions))
            
            # Apply price range filter
            if filters.get('price_range'):
                price_range = filters['price_range']
                if price_range.get('min') is not None:
                    db_query = db_query.filter(Product.price >= price_range['min'])
                if price_range.get('max') is not None:
                    db_query = db_query.filter(Product.price <= price_range['max'])
            
            # Apply condition filter
            if filters.get('condition'):
                db_query = db_query.filter(Product.condition == filters['condition'])
            
            # Apply brand filter
            if filters.get('brand'):
                brand = filters['brand']
                # Handle brand as either string or list
                if isinstance(brand, list):
                    # If it's a list, use OR condition for any matching brand
                    from sqlalchemy import or_
                    brand_conditions = [Product.brand.ilike(f"%{b}%") for b in brand if b]
                    if brand_conditions:
                        db_query = db_query.filter(or_(*brand_conditions))
                else:
                    # If it's a string, use simple LIKE
                    db_query = db_query.filter(Product.brand.ilike(f"%{brand}%"))
            
            # Apply category filter
            if filters.get('category'):
                db_query = db_query.filter(Product.category.ilike(f"%{filters['category']}%"))
            
            # Execute query and convert to dictionaries
            products = db_query.all()
            result = []
            for product in products:
                result.append({
                    "id": self._sanitize_text(product.id),
                    "name": self._sanitize_text(product.name),
                    "price": product.price,
                    "condition": self._sanitize_text(product.condition),
                    "seller_rating": product.seller_rating,
                    "category": self._sanitize_text(product.category),
                    "brand": self._sanitize_text(product.brand) if product.brand else None,
                    "image_url": self._sanitize_text(product.image_url) if product.image_url else None,
                    "url": self._sanitize_text(product.url) if product.url else None,
                    "description": self._sanitize_text(product.description) if product.description else None
                })
            
            return result
            
        except Exception as e:
            print(f"Error searching products: {e}")
            return []
        finally:
            session.close()
    
    def get_product_by_id(self, product_id: str) -> Optional[Dict]:
        """Get a specific product by ID"""
        session = self.get_session()
        try:
            product = session.query(Product).filter(Product.id == product_id).first()
            if product:
                return {
                    "id": self._sanitize_text(product.id),
                    "name": self._sanitize_text(product.name),
                    "price": product.price,
                    "condition": self._sanitize_text(product.condition),
                    "seller_rating": product.seller_rating,
                    "category": self._sanitize_text(product.category),
                    "brand": self._sanitize_text(product.brand) if product.brand else None,
                    "image_url": self._sanitize_text(product.image_url) if product.image_url else None,
                    "url": self._sanitize_text(product.url) if product.url else None,
                    "description": self._sanitize_text(product.description) if product.description else None
                }
            return None
        except Exception as e:
            print(f"Error getting product by ID: {e}")
            return None
        finally:
            session.close()
    
    def add_product(self, product_data: Dict) -> bool:
        """Add a new product to the database"""
        session = self.get_session()
        try:
            # Sanitize the data
            sanitized_data = self._sanitize_product_data(product_data)
            
            product = Product(
                id=sanitized_data["id"],
                name=sanitized_data["name"],
                price=sanitized_data["price"],
                condition=sanitized_data["condition"],
                seller_rating=sanitized_data["seller_rating"],
                category=sanitized_data["category"],
                brand=sanitized_data.get("brand"),
                image_url=sanitized_data.get("image_url"),
                url=sanitized_data.get("url"),
                description=sanitized_data.get("description")
            )
            session.add(product)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error adding product: {e}")
            return False
        finally:
            session.close()
    
    def get_all_products(self) -> List[Dict]:
        """Get all products from the database"""
        session = self.get_session()
        try:
            products = session.query(Product).all()
            result = []
            for product in products:
                result.append({
                    "id": self._sanitize_text(product.id),
                    "name": self._sanitize_text(product.name),
                    "price": product.price,
                    "condition": self._sanitize_text(product.condition),
                    "seller_rating": product.seller_rating,
                    "category": self._sanitize_text(product.category),
                    "brand": self._sanitize_text(product.brand) if product.brand else None,
                    "image_url": self._sanitize_text(product.image_url) if product.image_url else None,
                    "url": self._sanitize_text(product.url) if product.url else None,
                    "description": self._sanitize_text(product.description) if product.description else None
                })
            return result
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
        finally:
            session.close()
    
    def _extract_search_terms(self, query: str, filters: Dict[str, Any]) -> List[str]:
        """Extract search terms from query and filters"""
        terms = []
        
        # From query
        if query:
            query_words = re.findall(r'\w+', self._sanitize_text(query).lower())
            terms.extend(query_words)
        
        # From filters
        if filters.get('product_keywords'):
            for kw in filters['product_keywords']:
                if kw:
                    terms.append(self._sanitize_text(kw).lower())
        
        if filters.get('brand'):
            brand = filters['brand']
            # Handle brand as either string or list
            if isinstance(brand, list):
                for b in brand:
                    if b:
                        terms.append(self._sanitize_text(b).lower())
            else:
                terms.append(self._sanitize_text(brand).lower())
        
        if filters.get('category'):
            terms.append(self._sanitize_text(filters['category']).lower())
        
        # Remove duplicates and empty terms
        return list(set([term for term in terms if term]))
    
    def clear_all_products(self):
        """Delete all products from the database (for re-initializing sample data)"""
        session = self.get_session()
        try:
            session.query(Product).delete()
            session.commit()
            print("All products deleted from the database.")
        except Exception as e:
            session.rollback()
            print(f"Error clearing products: {e}")
        finally:
            session.close()

    def create_tables(self):
        """Create all tables in the database (for test compatibility)"""
        Base.metadata.create_all(bind=self.engine)

    def ensure_showcase_categories(self):
        """Ensure showcase categories have at least 4 products each. Add samples if missing."""
        showcase_categories = {
            "Electronics": [
                {
                    "id": "ent001",
                    "name": "Sony WH-1000XM5 Headphones",
                    "price": 42000,
                    "condition": "new",
                    "seller_rating": 4.9,
                    "category": "Electronics",
                    "brand": "Sony",
                    "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=150&h=150&fit=crop&crop=center",
                    "url": "https://jp.mercari.com/item/ent001",
                    "description": "Industry-leading noise canceling headphones."
                }
            ],
            "Entertainment": [
                {
                    "id": "ent002",
                    "name": "Nintendo Switch OLED",
                    "price": 35000,
                    "condition": "like_new",
                    "seller_rating": 4.8,
                    "category": "Entertainment",
                    "brand": "Nintendo",
                    "image_url": "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=150&h=150&fit=crop&crop=center",
                    "url": "https://jp.mercari.com/item/ent002",
                    "description": "Nintendo Switch OLED model, barely used."
                },
                {
                    "id": "ent003",
                    "name": "PlayStation 5 Console",
                    "price": 65000,
                    "condition": "very_good",
                    "seller_rating": 4.9,
                    "category": "Entertainment",
                    "brand": "Sony",
                    "image_url": "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=150&h=150&fit=crop&crop=center",
                    "url": "https://jp.mercari.com/item/ent003",
                    "description": "PS5 console with original accessories."
                }
            ],
            "Fashion": [
                {
                    "id": "fas001",
                    "name": "Uniqlo Ultra Light Down Jacket",
                    "price": 5000,
                    "condition": "good",
                    "seller_rating": 4.7,
                    "category": "Fashion",
                    "brand": "Uniqlo",
                    "image_url": "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=150&h=150&fit=crop&crop=center",
                    "url": "https://jp.mercari.com/item/fas001",
                    "description": "Lightweight and warm down jacket."
                }
            ],
            "Home & Beauty": [
                {
                    "id": "hb001",
                    "name": "Dyson Supersonic Hair Dryer",
                    "price": 32000,
                    "condition": "like_new",
                    "seller_rating": 4.8,
                    "category": "Home & Beauty",
                    "brand": "Dyson",
                    "image_url": "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=150&h=150&fit=crop&crop=center",
                    "url": "https://jp.mercari.com/item/hb001",
                    "description": "High-end hair dryer, barely used."
                },
                {
                    "id": "hb002",
                    "name": "Panasonic Nanoe Facial Steamer",
                    "price": 12000,
                    "condition": "new",
                    "seller_rating": 4.7,
                    "category": "Home & Beauty",
                    "brand": "Panasonic",
                    "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=150&h=150&fit=crop&crop=center",
                    "url": "https://jp.mercari.com/item/hb002",
                    "description": "Facial steamer for skincare routines."
                }
            ]
        }
        for cat, samples in showcase_categories.items():
            count = len([p for p in self.get_all_products() if p['category'].lower() == cat.lower()])
            if count < 2:
                for sample in samples:
                    self.add_product(sample)

    def map_category(self, category: str) -> str:
        """Map similar categories for display purposes."""
        mapping = {
            "home & kitchen": "Home & Beauty",
            "home & beauty": "Home & Beauty",
            "entertainment": "Entertainment",
            "gaming": "Entertainment"
        }
        return mapping.get(category.lower(), category)

    def ensure_all_products_have_images(self):
        """Ensure all products in the database have image URLs"""
        session = self.get_session()
        try:
            products = session.query(Product).all()
            image_urls = [
                "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1556821840-3a63f95609a7?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1515562141207-7a88fb7ce338?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=300&h=300&fit=crop&crop=center",
                "https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=300&h=300&fit=crop&crop=center"
            ]
            
            import random
            updated_count = 0
            for product in products:
                if not product.image_url or product.image_url.strip() == "":
                    product.image_url = random.choice(image_urls)
                    updated_count += 1
            
            session.commit()
            print(f"Updated {updated_count} products with image URLs")
            
        except Exception as e:
            session.rollback()
            print(f"Error updating product images: {e}")
        finally:
            session.close()
    
    def close(self):
        """Close database connections and clean up resources"""
        try:
            if hasattr(self, 'engine'):
                self.engine.dispose()
                print("Database connections closed")
        except Exception as e:
            print(f"Error closing database connections: {e}")

    def save_user_feedback(self, session_id: str, product_id: str, action_type: str, comment: str = None) -> bool:
        """Save user feedback (like, save, dismiss, etc.) for a product"""
        session = self.get_session()
        try:
            feedback = UserFeedback(
                session_id=session_id,
                product_id=product_id,
                action_type=action_type,
                comment=comment
            )
            session.add(feedback)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error saving user feedback: {e}")
            return False
        finally:
            session.close()

    def get_user_feedback(self, session_id: str, action_type: str = None) -> List[Dict]:
        """Fetch feedback for a session, optionally filtered by action_type"""
        session = self.get_session()
        try:
            query = session.query(UserFeedback).filter(UserFeedback.session_id == session_id)
            if action_type:
                query = query.filter(UserFeedback.action_type == action_type)
            feedbacks = query.order_by(UserFeedback.created_at.desc()).all()
            return [
                {
                    "id": str(f.id),
                    "session_id": f.session_id,
                    "product_id": f.product_id,
                    "action_type": f.action_type,
                    "comment": f.comment,
                    "created_at": f.created_at.isoformat() if f.created_at else None
                }
                for f in feedbacks
            ]
        except Exception as e:
            print(f"Error fetching user feedback: {e}")
            return []
        finally:
            session.close()

    def is_product_feedback(self, session_id: str, product_id: str, action_type: str) -> bool:
        """Check if a product has a given feedback (like, save, dismiss) for this session"""
        session = self.get_session()
        try:
            exists = session.query(UserFeedback).filter(
                UserFeedback.session_id == session_id,
                UserFeedback.product_id == product_id,
                UserFeedback.action_type == action_type
            ).first()
            return exists is not None
        except Exception as e:
            print(f"Error checking product feedback: {e}")
            return False
        finally:
            session.close()

    def get_feedback_product_ids(self, session_id: str, action_type: str) -> List[str]:
        """Get product_ids for a given feedback type (e.g., liked, saved) for this session"""
        session = self.get_session()
        try:
            results = session.query(UserFeedback.product_id).filter(
                UserFeedback.session_id == session_id,
                UserFeedback.action_type == action_type
            ).all()
            return [r[0] for r in results]
        except Exception as e:
            print(f"Error fetching feedback product ids: {e}")
            return []
        finally:
            session.close()

    # Cart Management Functions
    def add_to_cart(self, product: Dict, session_id: str) -> str:
        """Add a product to the cart for a session"""
        session = self.get_session()
        try:
            # Check if product is already in cart
            existing = session.query(CartItem).filter(
                CartItem.session_id == session_id,
                CartItem.product_id == product.get('id', '')
            ).first()
            
            if existing:
                return "Already in cart"
            
            # Add new cart item
            cart_item = CartItem(
                session_id=session_id,
                product_id=self._sanitize_text(product.get('id', '')),
                product_title=self._sanitize_text(product.get('name', '')),
                price=product.get('price', 0),
                image_url=self._sanitize_text(product.get('image_url', '')),
                condition=self._sanitize_text(product.get('condition', '')),
                category=self._sanitize_text(product.get('category', '')),
                brand=self._sanitize_text(product.get('brand', '')),
                url=self._sanitize_text(product.get('url', ''))
            )
            
            session.add(cart_item)
            session.commit()
            return "Added to cart"
            
        except Exception as e:
            session.rollback()
            print(f"Error adding to cart: {e}")
            return "Error adding to cart"
        finally:
            session.close()

    def get_cart_items(self, session_id: str) -> List[Dict]:
        """Get all cart items for a session"""
        session = self.get_session()
        try:
            cart_items = session.query(CartItem).filter(
                CartItem.session_id == session_id
            ).order_by(CartItem.added_at.desc()).all()
            
            return [
                {
                    "id": str(item.id),
                    "session_id": item.session_id,
                    "product_id": item.product_id,
                    "product_title": item.product_title,
                    "price": item.price,
                    "image_url": item.image_url,
                    "condition": item.condition,
                    "category": item.category,
                    "brand": item.brand,
                    "url": item.url,
                    "added_at": item.added_at.isoformat() if item.added_at else None
                }
                for item in cart_items
            ]
        except Exception as e:
            print(f"Error fetching cart items: {e}")
            return []
        finally:
            session.close()

    def remove_from_cart(self, product_id: str, session_id: str) -> bool:
        """Remove a product from the cart"""
        session = self.get_session()
        try:
            result = session.query(CartItem).filter(
                CartItem.session_id == session_id,
                CartItem.product_id == product_id
            ).delete()
            session.commit()
            return result > 0
        except Exception as e:
            session.rollback()
            print(f"Error removing from cart: {e}")
            return False
        finally:
            session.close()

    def is_in_cart(self, product_id: str, session_id: str) -> bool:
        """Check if a product is in the cart for a session"""
        session = self.get_session()
        try:
            exists = session.query(CartItem).filter(
                CartItem.session_id == session_id,
                CartItem.product_id == product_id
            ).first()
            return exists is not None
        except Exception as e:
            print(f"Error checking cart status: {e}")
            return False
        finally:
            session.close()

    def clear_cart(self, session_id: str) -> bool:
        """Clear all items from cart for a session"""
        session = self.get_session()
        try:
            result = session.query(CartItem).filter(
                CartItem.session_id == session_id
            ).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error clearing cart: {e}")
            return False
        finally:
            session.close()

    def get_cart_total(self, session_id: str) -> int:
        """Get the total price of all items in cart"""
        session = self.get_session()
        try:
            total = session.query(CartItem.price).filter(
                CartItem.session_id == session_id
            ).all()
            return sum(price[0] for price in total)
        except Exception as e:
            print(f"Error calculating cart total: {e}")
            return 0
        finally:
            session.close()