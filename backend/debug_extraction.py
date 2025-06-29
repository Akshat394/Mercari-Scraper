import asyncio
from playwright.async_api import async_playwright
from utils import get_random_user_agent, async_random_delay

async def debug_extraction():
    """Debug the exact HTML structure to find working selectors"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        # Set user agent
        await page.set_extra_http_headers({
            'User-Agent': get_random_user_agent()
        })
        
        # Go to Mercari search
        await page.goto("https://jp.mercari.com/search?keyword=iPhone", wait_until='domcontentloaded')
        await async_random_delay(5.0, 8.0)
        
        print("🔍 Debugging Mercari HTML structure...")
        print("=" * 60)
        
        # Find product containers
        items = await page.query_selector_all('[class*="item"]')
        print(f"Found {len(items)} items with '[class*=\"item\"]' selector")
        
        if len(items) > 0:
            first_item = items[0]
            
            print("\n📋 Inspecting first item structure:")
            print("-" * 40)
            
            # Get the HTML of the first item
            item_html = await first_item.inner_html()
            print(f"Item HTML (first 500 chars): {item_html[:500]}...")
            
            # Print all direct child divs' text
            print("\n🔎 All direct child <div> text content:")
            child_divs = await first_item.query_selector_all(':scope > div')
            for idx, div in enumerate(child_divs):
                try:
                    text = await div.text_content()
                    print(f"  Child div {idx}: {text.strip() if text else '[empty]'}")
                except Exception as e:
                    print(f"  Child div {idx}: [error: {e}]")
            
            # Try to find image as before
            print("\n🖼️ Looking for image...")
            img_elem = await first_item.query_selector('img')
            if img_elem:
                src = await img_elem.get_attribute('src')
                if src:
                    print(f"✅ Image found: {src[:100]}...")
                else:
                    print("❌ Image element found but no src attribute")
            else:
                print("❌ No image element found")
        
        print("\n" + "=" * 60)
        print("🔍 Manual inspection complete. Check the browser window.")
        
        # Keep browser open for manual inspection
        input("Press Enter to close browser...")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(debug_extraction()) 