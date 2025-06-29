# Backend package for Mercari Japan Shopping AI
# This file makes the backend directory a Python package

from .config import SessionLocal, engine
from .models import Product, Base
from .query import (
    get_all_products,
    get_products_by_tags,
    search_products_by_title,
    get_products_by_category,
    get_products_by_price_range,
    get_products_with_tags
)

__all__ = [
    'SessionLocal',
    'engine',
    'Product',
    'Base',
    'get_all_products',
    'get_products_by_tags',
    'search_products_by_title',
    'get_products_by_category',
    'get_products_by_price_range',
    'get_products_with_tags'
] 