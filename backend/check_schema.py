from .config import engine
from .models import Product, Base
from sqlalchemy import text

def check_database_schema():
    """Check the current database schema"""
    try:
        # Get table information
        result = engine.execute(text("""
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'products'
            ORDER BY ordinal_position
        """))
        
        print("📊 Current Database Schema:")
        print("=" * 50)
        
        columns = {}
        for row in result:
            table_name = row.table_name
            if table_name not in columns:
                columns[table_name] = []
            columns[table_name].append({
                'column': row.column_name,
                'type': row.data_type,
                'nullable': row.is_nullable
            })
        
        for table_name, cols in columns.items():
            print(f"\nTable: {table_name}")
            print("-" * 30)
            for col in cols:
                nullable = "NULL" if col['nullable'] == 'YES' else "NOT NULL"
                print(f"  {col['column']}: {col['type']} ({nullable})")
        
        # Check if seo_tags column exists
        result = engine.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'products' AND column_name = 'seo_tags'
        """))
        
        if result.fetchone():
            print("\n✅ seo_tags column exists!")
        else:
            print("\n❌ seo_tags column missing!")
            
    except Exception as e:
        print(f"❌ Error checking schema: {e}")

if __name__ == "__main__":
    check_database_schema() 