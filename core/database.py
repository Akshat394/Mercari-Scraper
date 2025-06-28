import os
import json
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
    
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
        
        # Initialize with sample data if empty
        self._initialize_sample_data()
    
    def get_session(self) -> Session:
        """Get a database session"""
        return self.SessionLocal()
    
    def _initialize_sample_data(self):
        """Initialize database with sample data if it's empty"""
        session = self.get_session()
        try:
            # Check if data already exists
            existing_count = session.query(Product).count()
            if existing_count > 0:
                return
            
            # Add sample data
            for product_data in SAMPLE_MERCARI_DATA:
                product = Product(
                    id=product_data["id"],
                    name=product_data["name"],
                    price=product_data["price"],
                    condition=product_data["condition"],
                    seller_rating=product_data["seller_rating"],
                    category=product_data["category"],
                    brand=product_data.get("brand"),
                    image_url=product_data.get("image_url"),
                    url=product_data.get("url"),
                    description=product_data.get("description")
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
                if price_range.get('min'):
                    db_query = db_query.filter(Product.price >= price_range['min'])
                if price_range.get('max'):
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
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "condition": product.condition,
                    "seller_rating": product.seller_rating,
                    "category": product.category,
                    "brand": product.brand,
                    "image_url": product.image_url,
                    "url": product.url,
                    "description": product.description
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
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "condition": product.condition,
                    "seller_rating": product.seller_rating,
                    "category": product.category,
                    "brand": product.brand,
                    "image_url": product.image_url,
                    "url": product.url,
                    "description": product.description
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
            product = Product(
                id=product_data["id"],
                name=product_data["name"],
                price=product_data["price"],
                condition=product_data["condition"],
                seller_rating=product_data["seller_rating"],
                category=product_data["category"],
                brand=product_data.get("brand"),
                image_url=product_data.get("image_url"),
                url=product_data.get("url"),
                description=product_data.get("description")
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
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "condition": product.condition,
                    "seller_rating": product.seller_rating,
                    "category": product.category,
                    "brand": product.brand,
                    "image_url": product.image_url,
                    "url": product.url,
                    "description": product.description
                })
            return result
        except Exception as e:
            print(f"Error getting all products: {e}")
            return []
        finally:
            session.close()
    
    def _extract_search_terms(self, query: str, filters: Dict[str, Any]) -> List[str]:
        """Extract search terms from query and filters"""
        import re
        terms = []
        
        # From query
        query_words = re.findall(r'\w+', query.lower())
        terms.extend(query_words)
        
        # From filters
        if filters.get('product_keywords'):
            terms.extend([kw.lower() for kw in filters['product_keywords']])
        
        if filters.get('brand'):
            terms.append(filters['brand'].lower())
        
        if filters.get('category'):
            terms.append(filters['category'].lower())
        
        return list(set(terms))  # Remove duplicates