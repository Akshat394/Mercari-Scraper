from config import engine
from models import Product, Base
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

if __name__ == '__main__':
    clean_products_table() 