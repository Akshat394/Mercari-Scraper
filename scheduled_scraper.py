import os
import sys
import time
from core.mercari_scraper import MercariScraper
from core.product_ranker import ProductRanker
from core.database import DatabaseManager
from dotenv import load_dotenv

# Load environment variables (for DATABASE_URL, etc.)
load_dotenv()

# You can customize these queries/categories as needed
QUERIES = [
    "iPhone", "Nintendo Switch", "MacBook", "PlayStation", "AirPods", "Louis Vuitton", "Rolex", "Supreme", "Chanel"
]
CATEGORIES = [
    "Electronics", "Gaming", "Fashion", "Watches", "Collectibles", "Trading Cards"
]

def main():
    print("Starting scheduled Mercari scraping job...")
    db = DatabaseManager(os.environ.get("DATABASE_URL"))
    scraper = MercariScraper(use_selenium=False)  # Use Playwright/requests for cloud compatibility
    ranker = ProductRanker()

    for query in QUERIES:
        print(f"Scraping for query: {query}")
        products = scraper.search_products(query)
        if not products:
            print(f"No products found for query: {query}")
            continue

        # Deduplicate and rank products
        ranked_products = ranker.rank_products(products, {"product_keywords": [query]})
        for product in ranked_products:
            # Use product['id'] as unique key; skip if already exists
            if db.get_product_by_id(product['id']):
                continue
            # Add product to database
            success = db.add_product(product)
            if success:
                print(f"Added product: {product['name']} (ID: {product['id']})")
            else:
                print(f"Failed to add product: {product['name']} (ID: {product['id']})")
        time.sleep(2)  # Be polite to Mercari

    print("Scheduled scraping job complete.")

if __name__ == "__main__":
    main() 