from config import engine
from sqlalchemy import text

def check_database_schema():
    """Check the actual database schema"""
    try:
        with engine.connect() as conn:
            # Get table info
            result = conn.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'products' 
                ORDER BY ordinal_position;
            """))
            
            print("📋 Current database schema for 'products' table:")
            print("=" * 60)
            for row in result:
                print(f"  {row[0]}: {row[1]} ({'NULL' if row[2] == 'YES' else 'NOT NULL'})")
            
            # Check if table exists
            result = conn.execute(text("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = 'products';
            """))
            
            if result.scalar() == 0:
                print("\n❌ Table 'products' does not exist!")
            else:
                print(f"\n✅ Table 'products' exists")
                
                # Count rows
                result = conn.execute(text("SELECT COUNT(*) FROM products;"))
                count = result.scalar()
                print(f"📊 Current row count: {count}")
                
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_database_schema() 