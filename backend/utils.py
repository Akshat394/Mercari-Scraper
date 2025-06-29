import asyncio
import random
import logging
from typing import Any, Callable
from functools import wraps
import time
import re
from typing import Optional, List, Dict
from datetime import datetime, timedelta
from sqlalchemy import text
from .config import SessionLocal
from .models import Product

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def retry_on_exception(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """Decorator to retry functions on exception with exponential backoff"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    
                    if attempt < max_retries - 1:
                        await asyncio.sleep(current_delay)
                        current_delay *= backoff
            
            logger.error(f"All {max_retries} attempts failed. Last exception: {last_exception}")
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Attempt {attempt + 1} failed: {e}")
                    
                    if attempt < max_retries - 1:
                        time.sleep(current_delay)
                        current_delay *= backoff
            
            logger.error(f"All {max_retries} attempts failed. Last exception: {last_exception}")
            raise last_exception
        
        # Return async wrapper if function is async, sync wrapper otherwise
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

def get_random_user_agent() -> str:
    """Get a random user agent string"""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59"
    ]
    return random.choice(user_agents)

def random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
    """Add a random delay to avoid rate limiting"""
    delay = random.uniform(min_delay, max_delay)
    time.sleep(delay)

async def async_random_delay(min_delay: float = 1.0, max_delay: float = 3.0):
    """Add a random delay asynchronously"""
    delay = random.uniform(min_delay, max_delay)
    await asyncio.sleep(delay)

def sanitize_text(text: str) -> str:
    """Sanitize text by removing null bytes and extra whitespace"""
    if not text:
        return ""
    
    # Remove null bytes and other control characters
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', str(text))
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_price_from_text(price_text: str) -> float:
    """Extract numeric price from text containing currency symbols"""
    if not price_text:
        return 0.0
    
    # Remove currency symbols and commas, extract numbers
    price_match = re.search(r'[\d,]+', price_text.replace('¥', '').replace('$', ''))
    if price_match:
        return float(price_match.group().replace(',', ''))
    return 0.0

def extract_condition_from_text(text: str) -> str:
    """Extract condition from product text"""
    if not text:
        return "unknown"
    
    text_lower = text.lower()
    
    condition_mapping = {
        "新品": "new",
        "未使用": "new",
        "new": "new",
        "like new": "like_new",
        "like-new": "like_new",
        "ほぼ新品": "like_new",
        "very good": "very_good",
        "very-good": "very_good",
        "良好": "very_good",
        "good": "good",
        "acceptable": "acceptable",
        "可": "acceptable"
    }
    
    for japanese, english in condition_mapping.items():
        if japanese in text_lower:
            return english
    
    return "unknown"

def extract_category_from_url(url: str) -> str:
    """Extract category from Mercari URL"""
    if not url:
        return "unknown"
    
    # Look for category patterns in URL
    category_patterns = [
        r'/category/([^/]+)',
        r'/search\?category=([^&]+)',
        r'/jp/category/([^/]+)'
    ]
    
    for pattern in category_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return "unknown" 