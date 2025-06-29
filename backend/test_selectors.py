import asyncio
from playwright.async_api import async_playwright
from utils import get_random_user_agent, async_random_delay

async def inspect_mercari_structure():
    """Inspect Mercari's HTML structure to find correct selectors"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # Show browser for inspection
        page = await browser.new_page()
        
        # Set user agent
        await page.set_extra_http_headers({
            'User-Agent': get_random_user_agent()
        })
        
        # Go to Mercari search
        await page.goto("https://jp.mercari.com/search?keyword=iPhone", wait_until='domcontentloaded')
        await async_random_delay(5.0, 8.0)
        
        print("🔍 Inspecting Mercari HTML structure...")
        print("=" * 50)
        
        # Try to find product containers
        selectors_to_try = [
            '[data-testid="item-cell"]',
            '.item-cell',
            '[class*="item"]',
            'li[data-testid*="item"]',
            '.search-result-item',
            '[data-testid*="item"]',
            'article',
            'li',
            '.item'
        ]
        
        for selector in selectors_to_try:
            try:
                items = await page.query_selector_all(selector)
                if items:
                    print(f"✅ Found {len(items)} items with selector: {selector}")
                    
                    # Inspect first item
                    if len(items) > 0:
                        first_item = items[0]
                        
                        # Try to find title
                        title_selectors = ['h3', 'h2', '.title', '[class*="title"]', 'a']
                        for title_sel in title_selectors:
                            title_elem = await first_item.query_selector(title_sel)
                            if title_elem:
                                title_text = await title_elem.text_content()
                                if title_text and len(title_text.strip()) > 5:
                                    print(f"   📝 Title found with '{title_sel}': {title_text[:50]}...")
                                    break
                        
                        # Try to find price
                        price_selectors = [
                            '[data-testid="item-price"]',
                            '.price',
                            '[class*="price"]',
                            '.item-price',
                            '[class*="Price"]'
                        ]
                        for price_sel in price_selectors:
                            price_elem = await first_item.query_selector(price_sel)
                            if price_elem:
                                price_text = await price_elem.text_content()
                                if price_text and '¥' in price_text:
                                    print(f"   💰 Price found with '{price_sel}': {price_text}")
                                    break
                        
                        # Try to find link
                        link_elem = await first_item.query_selector('a')
                        if link_elem:
                            href = await link_elem.get_attribute('href')
                            if href:
                                print(f"   🔗 Link found: {href[:50]}...")
                        
                        break
                else:
                    print(f"❌ No items found with selector: {selector}")
            except Exception as e:
                print(f"❌ Error with selector {selector}: {e}")
        
        print("=" * 50)
        print("🔍 Manual inspection complete. Check the browser window.")
        
        # Keep browser open for manual inspection
        input("Press Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(inspect_mercari_structure()) 