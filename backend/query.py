from config import SessionLocal
from models import Product
from sqlalchemy import func, or_, text

def get_products_by_tags(tags: list, limit=10):
    """Get products that have matching SEO tags"""
    session = SessionLocal()
    try:
        # Use PostgreSQL array overlap operator to find products with matching tags
        conditions = []
        for tag in tags:
            conditions.append(text("seo_tags && ARRAY[:tag]"))
        
        query = session.query(Product)
        for condition in conditions:
            query = query.filter(condition.bindparams(tag=tag))
        
        results = [p.__dict__ for p in query.limit(limit)]
        return results
    except Exception as e:
        print(f"Error in get_products_by_tags: {e}")
        # Fallback to name/description search
        conditions = []
        for tag in tags:
            conditions.append(Product.name.ilike(f"%{tag}%"))
            conditions.append(Product.description.ilike(f"%{tag}%"))
        
        q = session.query(Product).filter(or_(*conditions))
        results = [p.__dict__ for p in q.limit(limit)]
        return results
    finally:
        session.close()

def get_products_by_category(category: str, limit=10):
    session = SessionLocal()
    q = session.query(Product).filter(func.lower(Product.category) == category.lower())
    results = [p.__dict__ for p in q.limit(limit)]
    session.close()
    return results

def search_products_by_title(keyword: str, limit=10):
    session = SessionLocal()
    q = session.query(Product).filter(Product.name.ilike(f"%{keyword}%"))
    results = [p.__dict__ for p in q.limit(limit)]
    session.close()
    return results

def get_all_products(limit=50):
    """Get all products from database"""
    session = SessionLocal()
    q = session.query(Product).order_by(Product.id.desc()).limit(limit)
    results = [p.__dict__ for p in q]
    session.close()
    return results

def get_products_by_price_range(min_price=0, max_price=None, limit=20):
    """Get products within a price range"""
    session = SessionLocal()
    q = session.query(Product).filter(Product.price >= min_price)
    if max_price:
        q = q.filter(Product.price <= max_price)
    results = [p.__dict__ for p in q.order_by(Product.price.desc()).limit(limit)]
    session.close()
    return results

def get_products_with_tags(limit=20):
    """Get products that have SEO tags"""
    session = SessionLocal()
    try:
        q = session.query(Product).filter(
            text("seo_tags IS NOT NULL AND array_length(seo_tags, 1) > 0")
        ).limit(limit)
        results = [p.__dict__ for p in q]
        return results
    except Exception as e:
        print(f"Error getting products with tags: {e}")
        return []
    finally:
        session.close() 