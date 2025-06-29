import asyncio
import time
from typing import Dict, List, Optional
import logging
from playwright.async_api import async_playwright
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatScraper:
    """Fast real-time scraper for Chat Assistant using Playwright"""
    
    def __init__(self):
        self.base_url = "https://jp.mercari.com"
        self.browser = None
        self.context = None
        self.page = None
        
    async def initialize(self):
        """Initialize Playwright browser"""
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-web-security',
                    '--disable-features=VizDisplayCompositor'
                ]
            )
            self.context = await self.browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                viewport={'width': 1920, 'height': 1080}
            )
            self.page = await self.context.new_page()
            
            # Set extra headers
            await self.page.set_extra_http_headers({
                'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            logger.info("Playwright browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Playwright: {e}")
            return False
    
    async def search_products_fast(self, query: str, filters: Optional[Dict] = None, max_results: int = 5) -> List[Dict]:
        """
        Fast product search using Playwright
        Returns top results with real image URLs
        """
        if not await self.initialize():
            return []
        
        try:
            # Build search URL
            search_url = await self._build_search_url(query, filters)
            logger.info(f"Searching: {search_url}")
            
            # Navigate to search page
            await self.page.goto(search_url, wait_until='networkidle', timeout=10000)
            
            # Wait for products to load
            await self._wait_for_products()
            
            # Extract products
            products = await self._extract_products(max_results)
            
            logger.info(f"Found {len(products)} products")
            return products
            
        except Exception as e:
            logger.error(f"Error in fast search: {e}")
            return []
        finally:
            await self.cleanup()
    
    async def _build_search_url(self, query: str, filters: Optional[Dict]) -> str:
        """Build optimized search URL"""
        params = {
            "keyword": query,
            "sort": "created_time",
            "order": "desc",
            "status": "on_sale"
        }
        
        if filters:
            # Add category
            if filters.get("category"):
                params["category"] = filters["category"].lower()
            
            # Add price range
            if filters.get("price_range"):
                price_range = filters["price_range"]
                if price_range.get("min") is not None:
                    params["price_min"] = str(price_range["min"])
                if price_range.get("max") is not None:
                    params["price_max"] = str(price_range["max"])
            
            # Add condition
            if filters.get("condition"):
                params["condition"] = filters["condition"]
        
        # Build URL
        param_str = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.base_url}/search?{param_str}"
    
    async def _wait_for_products(self):
        """Wait for product elements to load"""
        selectors = [
            '[data-testid="item-cell"]',
            '.item-cell',
            '[data-testid="search-item"]',
            '.search-item',
            'li[data-testid*="item"]',
            '.mercari-item',
            '[data-testid="item"]',
            '.item',
            'article',
            '.product-item'
        ]
        
        for selector in selectors:
            try:
                await self.page.wait_for_selector(selector, timeout=5000)
                logger.info(f"Products loaded with selector: {selector}")
                return
            except:
                continue
        
        # Fallback: wait for any content
        await self.page.wait_for_selector('body', timeout=5000)
    
    async def _extract_products(self, max_results: int) -> List[Dict]:
        """Extract product information from the page"""
        try:
            # Try multiple selectors for product elements
            selectors = [
                '[data-testid="item-cell"]',
                '.item-cell',
                '[data-testid="search-item"]',
                '.search-item',
                'li[data-testid*="item"]',
                '.mercari-item',
                '[data-testid="item"]',
                '.item',
                'article',
                '.product-item'
            ]
            
            products = []
            for selector in selectors:
                elements = await self.page.query_selector_all(selector)
                if elements:
                    logger.info(f"Found {len(elements)} elements with selector: {selector}")
                    
                    for element in elements[:max_results]:
                        product = await self._extract_single_product(element)
                        if product:
                            products.append(product)
                            if len(products) >= max_results:
                                break
                    
                    if products:
                        break
            
            return products
            
        except Exception as e:
            logger.error(f"Error extracting products: {e}")
            return []
    
    async def _extract_single_product(self, element) -> Optional[Dict]:
        """Extract information from a single product element"""
        try:
            # Extract name/title
            name_selectors = [
                '[data-testid="item-name"]',
                '.item-name',
                'h3',
                'h2',
                '.title',
                '.name',
                'a[title]'
            ]
            
            name = None
            for selector in name_selectors:
                try:
                    name_elem = await element.query_selector(selector)
                    if name_elem:
                        name = await name_elem.text_content()
                        if name:
                            name = name.strip()
                            break
                except:
                    continue
            
            # Extract price
            price_selectors = [
                '[data-testid="price"]',
                '.price',
                '.item-price',
                '[data-testid="item-price"]',
                'span[data-testid*="price"]'
            ]
            
            price = None
            for selector in price_selectors:
                try:
                    price_elem = await element.query_selector(selector)
                    if price_elem:
                        price_text = await price_elem.text_content()
                        if price_text:
                            # Extract numeric price
                            price_match = re.search(r'¥?([0-9,]+)', price_text)
                            if price_match:
                                price = int(price_match.group(1).replace(',', ''))
                                break
                except:
                    continue
            
            # Extract image URL
            image_selectors = [
                'img[src]',
                'img[data-src]',
                '[data-testid="item-image"] img',
                '.item-image img'
            ]
            
            image_url = None
            for selector in image_selectors:
                try:
                    img_elem = await element.query_selector(selector)
                    if img_elem:
                        src = await img_elem.get_attribute('src')
                        if not src:
                            src = await img_elem.get_attribute('data-src')
                        
                        if src and self._is_valid_mercari_image(src):
                            image_url = self._clean_image_url(src)
                            break
                except:
                    continue
            
            # Extract condition
            condition_selectors = [
                '[data-testid="condition"]',
                '.condition',
                '.item-condition',
                'span[data-testid*="condition"]'
            ]
            
            condition = "good"  # Default
            for selector in condition_selectors:
                try:
                    condition_elem = await element.query_selector(selector)
                    if condition_elem:
                        condition_text = await condition_elem.text_content()
                        if condition_text:
                            condition = condition_text.strip().lower()
                            break
                except:
                    continue
            
            # Extract seller rating
            rating_selectors = [
                '[data-testid="seller-rating"]',
                '.seller-rating',
                '.rating',
                'span[data-testid*="rating"]'
            ]
            
            seller_rating = 4.0  # Default
            for selector in rating_selectors:
                try:
                    rating_elem = await element.query_selector(selector)
                    if rating_elem:
                        rating_text = await rating_elem.text_content()
                        if rating_text:
                            rating_match = re.search(r'([0-9.]+)', rating_text)
                            if rating_match:
                                seller_rating = float(rating_match.group(1))
                                break
                except:
                    continue
            
            # Extract product URL
            url_selectors = [
                'a[href]',
                '[data-testid="item-link"]',
                '.item-link'
            ]
            
            product_url = None
            for selector in url_selectors:
                try:
                    link_elem = await element.query_selector(selector)
                    if link_elem:
                        href = await link_elem.get_attribute('href')
                        if href:
                            if href.startswith('/'):
                                product_url = f"{self.base_url}{href}"
                            elif href.startswith('http'):
                                product_url = href
                            break
                except:
                    continue
            
            # Create product object
            if name and price:
                return {
                    "id": f"mercari_{int(time.time())}_{len(name)}",
                    "name": name,
                    "price": price,
                    "image_url": image_url or self._get_placeholder_image(),
                    "condition": condition,
                    "seller_rating": seller_rating,
                    "product_url": product_url,
                    "category": "Electronics",  # Default, could be enhanced
                    "brand": None,
                    "shipping_included": True
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting single product: {e}")
            return None
    
    def _is_valid_mercari_image(self, url: str) -> bool:
        """Check if URL is a valid Mercari image"""
        if not url:
            return False
        
        # Check for Mercari CDN patterns
        mercari_patterns = [
            'static.mercdn.net',
            'mercdn.net',
            'mercari.com',
            'mercdn.com'
        ]
        
        return any(pattern in url.lower() for pattern in mercari_patterns)
    
    def _clean_image_url(self, url: str) -> str:
        """Clean and optimize image URL"""
        if not url:
            return self._get_placeholder_image()
        
        # Remove query parameters that might cause issues
        if '?' in url:
            url = url.split('?')[0]
        
        # Ensure HTTPS
        if url.startswith('http://'):
            url = url.replace('http://', 'https://')
        
        return url
    
    def _get_placeholder_image(self) -> str:
        """Get placeholder image URL"""
        return "https://via.placeholder.com/300x300/1e293b/60a5fa?text=Product+Image"
    
    async def cleanup(self):
        """Clean up Playwright resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if hasattr(self, 'playwright'):
                await self.playwright.stop()
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")

# Synchronous wrapper for easier integration
class ChatScraperSync:
    """Synchronous wrapper for ChatScraper"""
    
    def __init__(self):
        self.scraper = ChatScraper()
    
    def search_products_fast(self, query: str, filters: Optional[Dict] = None, max_results: int = 5) -> List[Dict]:
        """Synchronous wrapper for fast product search"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(
                self.scraper.search_products_fast(query, filters, max_results)
            )
        except Exception as e:
            logger.error(f"Error in sync search: {e}")
            return []
        finally:
            try:
                loop.close()
            except:
                pass 