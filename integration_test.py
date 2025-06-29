#!/usr/bin/env python3
"""
Integration Test for Mercari Japan Shopping AI System
Tests all components: Database, Scraper, SEO Tagger, Query Functions, and Streamlit Integration
"""

import sys
import os
sys.path.append('backend')

def test_backend_integration():
    """Test backend components integration"""
    print("🔧 Testing Backend Integration...")
    
    try:
        # Test 1: Database connection
        from backend.config import SessionLocal
        session = SessionLocal()
        print("✅ Database connection successful")
        session.close()
        
        # Test 2: Query functions
        from backend.query import get_all_products, search_products_by_title, get_products_by_tags
        products = get_all_products(5)
        print(f"✅ Query functions working - Found {len(products)} products")
        
        # Test 3: Search functionality
        iphone_products = search_products_by_title("iPhone", 3)
        print(f"✅ Search working - Found {len(iphone_products)} iPhone products")
        
        # Test 4: Tag-based search
        tagged_products = get_products_by_tags(['apple', 'smartphone'], 3)
        print(f"✅ Tag search working - Found {len(tagged_products)} tagged products")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend integration failed: {e}")
        return False

def test_data_quality():
    """Test the quality of scraped data"""
    print("\n📊 Testing Data Quality...")
    
    try:
        from backend.query import get_all_products
        products = get_all_products(10)
        
        if not products:
            print("❌ No products found in database")
            return False
        
        # Check data completeness
        complete_products = 0
        for product in products:
            if (product.get('name') and 
                product.get('price') and 
                product.get('category')):
                complete_products += 1
        
        completion_rate = (complete_products / len(products)) * 100
        print(f"✅ Data completeness: {completion_rate:.1f}% ({complete_products}/{len(products)})")
        
        # Check price distribution
        prices = [p.get('price', 0) for p in products if p.get('price')]
        if prices:
            avg_price = sum(prices) / len(prices)
            print(f"✅ Average price: ¥{avg_price:,.0f}")
            print(f"✅ Price range: ¥{min(prices):,} - ¥{max(prices):,}")
        
        return completion_rate > 80  # At least 80% complete
        
    except Exception as e:
        print(f"❌ Data quality test failed: {e}")
        return False

def test_seo_tags():
    """Test SEO tagging functionality"""
    print("\n🏷️ Testing SEO Tags...")
    
    try:
        from backend.query import get_products_with_tags
        tagged_products = get_products_with_tags(5)
        
        if tagged_products:
            print(f"✅ Found {len(tagged_products)} products with SEO tags")
            
            # Show sample tags
            for product in tagged_products[:3]:
                tags = product.get('seo_tags', [])
                if tags:
                    print(f"  - {product['name'][:40]}... Tags: {tags[:3]}")
            
            return True
        else:
            print("⚠️ No products with SEO tags found")
            return False
            
    except Exception as e:
        print(f"❌ SEO tags test failed: {e}")
        return False

def test_streamlit_integration():
    """Test Streamlit app integration"""
    print("\n🎨 Testing Streamlit Integration...")
    
    try:
        # Test imports
        import streamlit as st
        print("✅ Streamlit import successful")
        
        # Test backend imports in app context
        sys.path.append('backend')
        from backend.query import get_all_products
        products = get_all_products(1)
        print(f"✅ Backend integration in Streamlit context working")
        
        return True
        
    except Exception as e:
        print(f"❌ Streamlit integration failed: {e}")
        return False

def main():
    """Run all integration tests"""
    print("🚀 Mercari Japan Shopping AI - Integration Test")
    print("=" * 60)
    
    tests = [
        ("Backend Integration", test_backend_integration),
        ("Data Quality", test_data_quality),
        ("SEO Tags", test_seo_tags),
        ("Streamlit Integration", test_streamlit_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 INTEGRATION TEST SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! Your system is ready for production!")
        return True
    else:
        print("⚠️ Some tests failed. Please check the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 