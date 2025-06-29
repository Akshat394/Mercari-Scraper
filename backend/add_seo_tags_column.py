from config import SessionLocal
from sqlalchemy import text

def add_seo_tags_column():
    """Add seo_tags column to the products table"""
    session = SessionLocal()
    try:
        # Add the seo_tags column as a PostgreSQL array
        session.execute(text("""
            ALTER TABLE products 
            ADD COLUMN IF NOT EXISTS seo_tags TEXT[]
        """))
        session.commit()
        print("✅ Successfully added seo_tags column to products table")
        
        # Verify the column was added
        result = session.execute(text("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'seo_tags'
        """))
        
        if result.fetchone():
            print("✅ seo_tags column verified in database")
        else:
            print("❌ seo_tags column not found")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error adding seo_tags column: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    add_seo_tags_column() 