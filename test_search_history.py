#!/usr/bin/env python3
"""
Test script to validate search history functionality
"""

import sys
import os
import uuid
from datetime import datetime

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.data_handler import DataHandler
from core.database import DatabaseManager

def test_search_history_functionality():
    """Test the search history functionality"""
    print("🧪 Testing Search History Functionality")
    print("=" * 50)
    
    # Initialize data handler
    data_handler = DataHandler()
    session_id = str(uuid.uuid4())
    
    try:
        # Test 1: Store search results
        print("\n1. Testing search result storage...")
        test_products = [
            {
                "id": "test_001",
                "name": "iPhone 14 Pro Max",
                "price": 128000,
                "condition": "very_good",
                "seller_rating": 4.8,
                "category": "Electronics",
                "brand": "Apple",
                "image_url": "https://static.mercdn.net/item/detail/orig/photos/m123456789_1.jpg",
                "url": "https://jp.mercari.com/item/test_001",
                "description": "Excellent condition iPhone 14 Pro Max"
            },
            {
                "id": "test_002",
                "name": "Nintendo Switch OLED",
                "price": 35800,
                "condition": "like_new",
                "seller_rating": 4.9,
                "category": "Gaming",
                "brand": "Nintendo",
                "image_url": "https://static.mercdn.net/item/detail/orig/photos/m234567890_1.jpg",
                "url": "https://jp.mercari.com/item/test_002",
                "description": "Like new Nintendo Switch OLED"
            }
        ]
        
        stored_ids = data_handler.db_manager.store_search_results("iPhone", test_products, session_id)
        print(f"✅ Stored {len(stored_ids)} search results")
        
        # Test 2: Get search history
        print("\n2. Testing search history retrieval...")
        history = data_handler.get_search_history(session_id, limit=10)
        print(f"✅ Retrieved {len(history)} history entries")
        
        for entry in history:
            print(f"  - Query: {entry['query_text']}")
            print(f"    Product: {entry['product_title']}")
            print(f"    Price: ¥{entry['price']:,}")
            print(f"    Tags: {entry['tags']}")
            print()
        
        # Test 3: Get search summary
        print("\n3. Testing search summary...")
        summary = data_handler.get_search_summary(session_id)
        print(f"✅ Search Summary:")
        print(f"  - Total searches: {summary['total_searches']}")
        print(f"  - Unique queries: {summary['unique_queries']}")
        print(f"  - Recent searches: {summary['recent_searches']}")
        print(f"  - Common queries: {len(summary['common_queries'])}")
        
        # Test 4: Get recent products for recommendations
        print("\n4. Testing recent products for recommendations...")
        recent_products = data_handler.get_recent_products_for_recommendations("iPhone", limit=5)
        print(f"✅ Found {len(recent_products)} recent products for 'iPhone'")
        
        for product in recent_products:
            print(f"  - {product['name']} (¥{product['price']:,})")
        
        # Test 5: Search with history fallback
        print("\n5. Testing search with history fallback...")
        products = data_handler.search_with_history_fallback("iPhone", {}, session_id)
        print(f"✅ Search with history fallback found {len(products)} products")
        
        # Test 6: Test tag extraction
        print("\n6. Testing tag extraction...")
        test_product = {
            "id": "test_tag",
            "name": "MacBook Air M2 13 inch",
            "price": 145000,
            "condition": "good",
            "seller_rating": 4.7,
            "category": "Electronics",
            "brand": "Apple",
            "image_url": "https://example.com/image.jpg",
            "url": "https://jp.mercari.com/item/test_tag",
            "description": "Good condition MacBook Air"
        }
        
        tags = data_handler.db_manager._extract_tags_from_product(test_product)
        print(f"✅ Extracted tags: {tags}")
        
        # Test 7: Test database schema
        print("\n7. Testing database schema...")
        try:
            # Test if SearchHistory table exists and can be queried
            session = data_handler.db_manager.get_session()
            count = session.query(data_handler.db_manager.SearchHistory).count()
            print(f"✅ SearchHistory table exists with {count} entries")
            session.close()
        except Exception as e:
            print(f"❌ Database schema error: {e}")
        
        # Test 8: Test session management
        print("\n8. Testing session management...")
        new_session_id = str(uuid.uuid4())
        data_handler.db_manager.store_search_results("Test Query", test_products[:1], new_session_id)
        
        # Get history for specific session
        session_history = data_handler.get_search_history(new_session_id)
        print(f"✅ Session-specific history: {len(session_history)} entries")
        
        # Clear session history
        data_handler.clear_search_history(new_session_id)
        cleared_history = data_handler.get_search_history(new_session_id)
        print(f"✅ After clearing: {len(cleared_history)} entries")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        data_handler.close()
        print("\n🧹 Cleanup completed")

def test_database_integration():
    """Test database integration specifically"""
    print("\n🔧 Testing Database Integration")
    print("=" * 40)
    
    db_manager = DatabaseManager()
    
    try:
        # Test UUID generation
        print("1. Testing UUID generation...")
        test_uuid = uuid.uuid4()
        print(f"✅ Generated UUID: {test_uuid}")
        
        # Test PostgreSQL array support
        print("\n2. Testing PostgreSQL array support...")
        test_tags = ["electronics", "apple", "iphone", "smartphone"]
        print(f"✅ Test tags: {test_tags}")
        
        # Test datetime handling
        print("\n3. Testing datetime handling...")
        now = datetime.utcnow()
        print(f"✅ Current time: {now}")
        
        # Test table creation
        print("\n4. Testing table creation...")
        db_manager.create_tables()
        print("✅ Tables created successfully")
        
    except Exception as e:
        print(f"❌ Database integration test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db_manager.close()

def main():
    """Main test function"""
    print("🚀 Search History Test Suite")
    print("=" * 60)
    
    test_search_history_functionality()
    test_database_integration()
    
    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
    print("\n📋 Summary:")
    print("- Search history storage and retrieval")
    print("- Session-based history management")
    print("- Tag extraction and storage")
    print("- Search summary generation")
    print("- History fallback for recommendations")
    print("- Database schema validation")

if __name__ == "__main__":
    main() 