#!/usr/bin/env python3
"""
Test script to validate Mercari image URL extraction
This script tests the enhanced scraper's ability to extract real image URLs
"""

import sys
import os
import requests
from PIL import Image
from io import BytesIO
import time

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.mercari_scraper import MercariScraper

def test_image_url_validation(image_url: str) -> bool:
    """
    Test if an image URL is valid and returns an actual image
    """
    try:
        print(f"Testing image URL: {image_url}")
        
        # Make request to image URL
        response = requests.get(image_url, timeout=10, stream=True)
        response.raise_for_status()
        
        # Check if response is actually an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            print(f"❌ Not an image: {content_type}")
            return False
        
        # Try to open with PIL to validate it's a real image
        img = Image.open(BytesIO(response.content))
        print(f"✅ Valid image: {img.format} {img.size}")
        return True
        
    except Exception as e:
        print(f"❌ Error validating image: {e}")
        return False

def test_mercari_image_extraction():
    """
    Test the Mercari scraper's image extraction functionality
    """
    print("🧪 Testing Mercari Image URL Extraction")
    print("=" * 50)
    
    # Initialize scraper
    scraper = MercariScraper(use_selenium=False)  # Use requests for testing
    
    try:
        # Test search functionality
        print("\n1. Testing product search with image extraction...")
        test_queries = ["iPhone", "Nintendo Switch", "MacBook"]
        
        for query in test_queries:
            print(f"\n🔍 Searching for: {query}")
            products = scraper.search_products(query)
            
            if not products:
                print(f"❌ No products found for '{query}'")
                continue
            
            print(f"✅ Found {len(products)} products")
            
            # Test image URLs for each product
            valid_images = 0
            for i, product in enumerate(products[:3]):  # Test first 3 products
                print(f"\n  Product {i+1}: {product.get('name', 'Unknown')}")
                
                image_url = product.get('image_url')
                if not image_url:
                    print("  ❌ No image URL found")
                    continue
                
                print(f"  📸 Image URL: {image_url}")
                
                # Validate the image URL
                if test_image_url_validation(image_url):
                    valid_images += 1
                    print(f"  ✅ Image URL is valid")
                else:
                    print(f"  ❌ Image URL is invalid")
                
                time.sleep(1)  # Be nice to servers
            
            print(f"\n📊 Results for '{query}': {valid_images}/{min(3, len(products))} valid images")
        
        # Test individual product details
        print("\n2. Testing individual product detail extraction...")
        test_product_id = "sample1"
        product_details = scraper.get_product_details(test_product_id)
        
        if product_details:
            print(f"✅ Product details retrieved for ID: {test_product_id}")
            image_url = product_details.get('image_url')
            if image_url:
                print(f"📸 Detail image URL: {image_url}")
                if test_image_url_validation(image_url):
                    print("✅ Detail image URL is valid")
                else:
                    print("❌ Detail image URL is invalid")
            else:
                print("❌ No image URL in product details")
        else:
            print(f"❌ Failed to get product details for ID: {test_product_id}")
        
        # Test Mercari CDN URL patterns
        print("\n3. Testing Mercari CDN URL pattern validation...")
        test_urls = [
            "https://static.mercdn.net/item/detail/orig/photos/m123456789_1.jpg",
            "https://static.mercdn.net/item/detail/orig/photos/m234567890_1.jpg",
            "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=300&h=300&fit=crop&crop=center",
            "https://example.com/fake-image.jpg",
            "https://static.mercdn.net/fake/path/image.jpg"
        ]
        
        for url in test_urls:
            is_valid = scraper._is_valid_mercari_image_url(url)
            print(f"URL: {url}")
            print(f"Valid Mercari URL: {'✅' if is_valid else '❌'}")
            print()
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        scraper.close()
        print("\n🧹 Cleanup completed")

def test_html_parsing_with_sample_data():
    """
    Test HTML parsing with sample HTML data
    """
    print("\n4. Testing HTML parsing with sample data...")
    
    # Sample HTML that might be returned by Mercari
    sample_html = """
    <div class="item-cell" data-testid="item-cell">
        <img src="https://static.mercdn.net/item/detail/orig/photos/m123456789_1.jpg" 
             alt="Product Image" class="item-image">
        <div class="item-info">
            <h3 class="item-name">iPhone 14 Pro Max</h3>
            <div class="price">¥128,000</div>
            <div class="condition">新品</div>
        </div>
    </div>
    <div class="item-cell" data-testid="item-cell">
        <img data-src="https://static.mercdn.net/item/detail/orig/photos/m234567890_1.jpg" 
             alt="Product Image" class="item-image">
        <div class="item-info">
            <h3 class="item-name">Nintendo Switch</h3>
            <div class="price">¥35,800</div>
            <div class="condition">良好</div>
        </div>
    </div>
    """
    
    scraper = MercariScraper(use_selenium=False)
    
    try:
        # Parse the sample HTML
        products = scraper._parse_mercari_html(sample_html)
        
        print(f"✅ Parsed {len(products)} products from sample HTML")
        
        for i, product in enumerate(products):
            print(f"\nProduct {i+1}:")
            print(f"  Name: {product.get('name')}")
            print(f"  Price: {product.get('price')}")
            print(f"  Image URL: {product.get('image_url')}")
            print(f"  Condition: {product.get('condition')}")
            
            # Test the extracted image URL
            image_url = product.get('image_url')
            if image_url:
                if test_image_url_validation(image_url):
                    print(f"  ✅ Image URL is valid")
                else:
                    print(f"  ❌ Image URL is invalid")
    
    except Exception as e:
        print(f"❌ HTML parsing test failed: {e}")
    
    finally:
        scraper.close()

def main():
    """
    Main test function
    """
    print("🚀 Mercari Image URL Extraction Test Suite")
    print("=" * 60)
    
    # Run all tests
    test_mercari_image_extraction()
    test_html_parsing_with_sample_data()
    
    print("\n" + "=" * 60)
    print("🎉 Test suite completed!")
    print("\n📋 Summary:")
    print("- Enhanced scraper supports both BeautifulSoup and Selenium")
    print("- Image URL extraction with multiple fallback strategies")
    print("- Validation of Mercari CDN URLs")
    print("- Graceful fallback to placeholder images")
    print("- Comprehensive error handling and logging")

if __name__ == "__main__":
    main() 