from .config import engine
from .models import Product, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

Session = sessionmaker(bind=engine)

def clean_products_table():
    session = Session()
    try:
        session.execute(text('TRUNCATE TABLE products RESTART IDENTITY CASCADE;'))
        session.commit()
        print('✅ Products table cleaned.')
    except Exception as e:
        session.rollback()
        print(f'Error cleaning products table: {e}')
    finally:
        session.close()

def clean_database():
    """Clean all data from the database"""
    try:
        # Delete all products
        with engine.connect() as conn:
            result = conn.execute(text("DELETE FROM products"))
            conn.commit()
            print(f"✅ Deleted {result.rowcount} products from database")
            
    except Exception as e:
        print(f"❌ Error cleaning database: {e}")

if __name__ == '__main__':
    clean_products_table()
    clean_database() 