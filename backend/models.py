from sqlalchemy import Column, String, Float, DateTime, JSON, create_engine, Index, Text, Integer, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
import uuid
from datetime import datetime

Base = declarative_base()

class Product(Base):
    __tablename__ = 'products'

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)  # This is the title
    price = Column(Integer, nullable=False)
    condition = Column(String, nullable=False)
    seller_rating = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    brand = Column(String)
    image_url = Column(String)
    url = Column(String)  # This is the product_url
    description = Column(Text)
    seo_tags = Column(ARRAY(String))  # New column for SEO tags

# Create indexes for better search performance
Index('ix_products_name', Product.name)
Index('ix_products_category', Product.category)
Index('ix_products_price', Product.price) 