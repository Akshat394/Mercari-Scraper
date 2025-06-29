from query import *

def test_queries():
    print("🔍 Testing Query Functions with Scraped Data...")
    
    # Test 1: Get all products
    print("\n1. Getting all products (first 5):")
    all_products = get_all_products(5)
    for p in all_products:
        print(f"  - {p['name'][:50]}... (¥{p['price']})")
    
    # Test 2: Search by keyword
    print("\n2. Searching for 'iPhone':")
    iphone_products = search_products_by_title("iPhone", 3)
    for p in iphone_products:
        print(f"  - {p['name'][:50]}... (¥{p['price']})")
    
    # Test 3: Search by tags
    print("\n3. Searching by tags ['apple', 'smartphone']:")
    tagged_products = get_products_by_tags(['apple', 'smartphone'], 3)
    for p in tagged_products:
        print(f"  - {p['name'][:50]}... (¥{p['price']})")
    
    # Test 4: Price range
    print("\n4. Products under ¥10,000:")
    cheap_products = get_products_by_price_range(0, 10000, 3)
    for p in cheap_products:
        print(f"  - {p['name'][:50]}... (¥{p['price']})")
    
    print("\n✅ Query tests completed!")

if __name__ == "__main__":
    test_queries() 