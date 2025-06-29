import asyncio
import time
import random
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from playwright.async_api import async_playwright, Page, Browser
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from config import engine, SessionLocal, SCRAPER_CONFIG, MERCARI_BASE_URL, MERCARI_SEARCH_URL
from models import Product, Base
from utils import (
    retry_on_exception, get_random_user_agent, async_random_delay,
    sanitize_text, extract_price_from_text, extract_condition_from_text,
    extract_category_from_url, logger
)

# Create tables
Base.metadata.create_all(bind=engine)

class MercariScraper:
    """Playwright-based scraper for Mercari Japan"""
    
    def __init__(self):
        self.session = SessionLocal()
        self.scraped_count = 0
        self.duplicate_count = 0
        self.error_count = 0
        
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=SCRAPER_CONFIG["headless"]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self, 'browser'):
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
        if hasattr(self, 'session'):
            self.session.close()
    
    async def setup_page(self) -> Page:
        """Setup a new page with stealth settings"""
        page = await self.browser.new_page()
        
        # Set random user agent
        await page.set_extra_http_headers({
            'User-Agent': get_random_user_agent()
        })
        
        # Set viewport
        await page.set_viewport_size({"width": 1920, "height": 1080})
        
        # Add stealth settings
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined,
            });
        """)
        
        return page
    
    @retry_on_exception(max_retries=2, delay=5.0)
    async def scrape_product_details(self, page: Page, product_url: str) -> Dict:
        """Scrape detailed product information from product page"""
        try:
            await page.goto(product_url, wait_until='domcontentloaded', timeout=15000)
            await async_random_delay(2.0, 4.0)
            
            # Extract detailed information
            details = {}
            
            # Title - try multiple selectors
            title_selectors = [
                'h1[data-testid="item-name"]',
                'h1',
                '[data-testid="item-name"]',
                '.item-name'
            ]
            for selector in title_selectors:
                title_elem = await page.query_selector(selector)
                if title_elem:
                    details['title'] = await title_elem.text_content()
                    break
            
            # Price - try multiple selectors
            price_selectors = [
                '[data-testid="price"]',
                '.price',
                '[class*="price"]'
            ]
            for selector in price_selectors:
                price_elem = await page.query_selector(selector)
                if price_elem:
                    price_text = await price_elem.text_content()
                    details['price'] = extract_price_from_text(price_text)
                    break
            
            # Condition - try multiple selectors
            condition_selectors = [
                '[data-testid="item-condition"]',
                '.condition',
                '[class*="condition"]'
            ]
            for selector in condition_selectors:
                condition_elem = await page.query_selector(selector)
                if condition_elem:
                    condition_text = await condition_elem.text_content()
                    details['condition'] = extract_condition_from_text(condition_text)
                    break
            
            # Seller rating
            rating_selectors = [
                '[data-testid="seller-rating"]',
                '.rating',
                '[class*="rating"]'
            ]
            for selector in rating_selectors:
                rating_elem = await page.query_selector(selector)
                if rating_elem:
                    rating_text = await rating_elem.text_content()
                    try:
                        details['seller_rating'] = float(rating_text.replace('★', '').strip())
                    except:
                        details['seller_rating'] = None
                    break
            
            # Description
            desc_selectors = [
                '[data-testid="item-description"]',
                '.description',
                '[class*="description"]'
            ]
            for selector in desc_selectors:
                desc_elem = await page.query_selector(selector)
                if desc_elem:
                    details['description'] = await desc_elem.text_content()
                    break
            
            # Category
            category_selectors = [
                '[data-testid="category"]',
                '.category',
                '[class*="category"]'
            ]
            for selector in category_selectors:
                category_elem = await page.query_selector(selector)
                if category_elem:
                    details['category'] = await category_elem.text_content()
                    break
            
            return details
            
        except Exception as e:
            logger.error(f"Error scraping product details from {product_url}: {e}")
            return {}
    
    async def scrape_search_page(self, page: Page, keyword: str, page_num: int = 1) -> List[Dict]:
        """Scrape products from a search results page"""
        products = []
        
        try:
            # Construct search URL
            search_url = f"{MERCARI_SEARCH_URL}?keyword={keyword}"
            if page_num > 1:
                search_url += f"&page={page_num}"
            
            logger.info(f"Scraping page {page_num} for keyword: {keyword}")
            
            # Use domcontentloaded instead of networkidle for faster loading
            await page.goto(search_url, wait_until='domcontentloaded', timeout=20000)
            await async_random_delay(3.0, 6.0)
            
            # Wait for product items to load - use the working selector
            working_selector = '[class*="item"]'
            try:
                await page.wait_for_selector(working_selector, timeout=10000)
            except:
                logger.warning(f"No product items found on page {page_num} for keyword: {keyword}")
                return products
            
            # Scroll to load more items
            await self._scroll_page(page)
            
            # Get all product items using the working selector
            items = await page.query_selector_all(working_selector)
            logger.info(f"Found {len(items)} items on page {page_num}")
            
            for item in items:
                try:
                    product_data = await self._extract_product_from_item(item, page)
                    if product_data:
                        products.append(product_data)
                except Exception as e:
                    logger.error(f"Error extracting product: {e}")
                    self.error_count += 1
                    continue
            
        except Exception as e:
            logger.error(f"Error scraping search page {page_num}: {e}")
        
        return products
    
    async def _scroll_page(self, page: Page):
        """Scroll page to load more content"""
        try:
            # Scroll down multiple times to trigger lazy loading
            for i in range(2):
                await page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                await async_random_delay(2.0, 4.0)
                
                # Wait for new content to load
                await page.wait_for_timeout(3000)
        except Exception as e:
            logger.warning(f"Error during page scrolling: {e}")
    
    async def _extract_product_from_item(self, item, page: Page) -> Optional[Dict]:
        """Extract product data from a single item element"""
        try:
            # Image and title from img tag
            img_elem = await item.query_selector('img')
            image_url = None
            title = None
            if img_elem:
                image_url = await img_elem.get_attribute('src')
                title = await img_elem.get_attribute('alt')
                if image_url and 'placeholder' in image_url.lower():
                    image_url = None
            if not title or not image_url:
                return None
            title = sanitize_text(title)
            
            # Price from third child div (index 2)
            child_divs = await item.query_selector_all(':scope > div')
            price = 0
            if len(child_divs) > 2:
                price_text = await child_divs[2].text_content()
                if price_text:
                    price = int(extract_price_from_text(price_text))
            
            # Product URL: try to find closest ancestor a, or skip if not found
            product_url = None
            link_elem = await item.query_selector('a')
            if link_elem:
                href = await link_elem.get_attribute('href')
                if href:
                    product_url = f"{MERCARI_BASE_URL}{href}" if href.startswith('/') else href
            # If not found, skip
            if not product_url:
                product_url = None
            
            # Basic product data - using existing schema field names
            product_data = {
                'id': str(uuid.uuid4()),  # Generate string ID
                'name': title,  # Use 'name' instead of 'title'
                'price': price,
                'condition': 'unknown',  # Default value for existing schema
                'seller_rating': 0.0,  # Default value for existing schema
                'category': extract_category_from_url(product_url) if product_url else 'unknown',
                'brand': None,  # Will be extracted later if needed
                'image_url': image_url,
                'url': product_url,  # Use 'url' instead of 'product_url'
                'description': None
            }
            
            return product_data
            
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None
    
    async def scrape_products(self, keywords: List[str], pages_per_keyword: int = 2) -> Dict:
        """Main scraping function"""
        page = await self.setup_page()
        
        try:
            for keyword in keywords:
                logger.info(f"Starting to scrape keyword: {keyword}")
                
                for page_num in range(1, pages_per_keyword + 1):
                    products = await self.scrape_search_page(page, keyword, page_num)
                    
                    # Save products to database
                    for product_data in products:
                        await self._save_product(product_data)
                    
                    # Add longer delay between pages
                    if page_num < pages_per_keyword:
                        await async_random_delay(8.0, 15.0)
                
                # Add longer delay between keywords
                if keyword != keywords[-1]:
                    await async_random_delay(15.0, 25.0)
        
        finally:
            await page.close()
        
        return {
            'scraped_count': self.scraped_count,
            'duplicate_count': self.duplicate_count,
            'error_count': self.error_count
        }
    
    async def _save_product(self, product_data: Dict):
        """Save product to database"""
        try:
            # Create Product object with existing schema
            product = Product(
                id=product_data.get('id', str(uuid.uuid4())),
                name=sanitize_text(product_data.get('name', '')),
                price=product_data.get('price', 0),
                condition=sanitize_text(product_data.get('condition', 'unknown')),
                seller_rating=product_data.get('seller_rating', 0.0),
                category=sanitize_text(product_data.get('category', 'unknown')),
                brand=sanitize_text(product_data.get('brand')),
                image_url=sanitize_text(product_data.get('image_url')),
                url=sanitize_text(product_data.get('url')),
                description=sanitize_text(product_data.get('description'))
            )
            
            self.session.add(product)
            self.session.commit()
            self.scraped_count += 1
            
            if self.scraped_count % 10 == 0:
                logger.info(f"Scraped {self.scraped_count} products so far...")
                
        except IntegrityError:
            self.session.rollback()
            self.duplicate_count += 1
        except Exception as e:
            self.session.rollback()
            logger.error(f"Error saving product: {e}")
            self.error_count += 1

async def main():
    """Main function to run the scraper"""
    # Reduced keywords and pages for testing
    keywords = [
        "スマートフォン",  # Smartphone
        "iPhone", 
        "Android",
        "ノートPC",  # Laptop
        "MacBook"
    ]
    
    async with MercariScraper() as scraper:
        results = await scraper.scrape_products(keywords, pages_per_keyword=2)
        
        logger.info("Scraping completed!")
        logger.info(f"Total scraped: {results['scraped_count']}")
        logger.info(f"Duplicates skipped: {results['duplicate_count']}")
        logger.info(f"Errors: {results['error_count']}")

if __name__ == "__main__":
    asyncio.run(main()) 