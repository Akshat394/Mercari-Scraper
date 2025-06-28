import os
import json
import re
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
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

class DatabaseManager:
    """Manages database connections and operations for Mercari products"""
    
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
                db_query = db_query.filter(Product.brand.ilike(f"%{filters['brand']}%"))
            
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
            terms.append(self._sanitize_text(filters['brand']).lower())
        
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