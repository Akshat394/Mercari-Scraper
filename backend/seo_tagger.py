from .models import Product
from .config import SessionLocal
from sqlalchemy import or_, text
import re

# Simple keyword-to-tag mapping (expand as needed)
KEYWORD_TAG_MAP = {
    "iphone": ["apple", "smartphone", "ios"],
    "android": ["android", "smartphone"],
    "switch": ["gaming", "nintendo", "console"],
    "macbook": ["apple", "laptop", "macos"],
    "バッグ": ["fashion", "bag"],
    "イヤホン": ["electronics", "audio", "earbuds"],
    "airpods": ["apple", "audio", "earbuds"],
    "カメラ": ["camera", "photography"],
    "時計": ["watch", "fashion"],
    "財布": ["wallet", "fashion"]
}

def rule_based_tags(name: str, description: str = ""):
    name_lower = name.lower() if name else ""
    desc_lower = description.lower() if description else ""
    tags = set()
    for keyword, mapped_tags in KEYWORD_TAG_MAP.items():
        if keyword in name_lower or keyword in desc_lower:
            tags.update(mapped_tags)
    # Add keywords from name (split by space, remove short words)
    for word in re.findall(r"\w+", name_lower):
        if len(word) > 2:
            tags.add(word)
    return list(tags)

def tag_unprocessed_products(batch_size=100):
    """Tag products that don't have SEO tags yet"""
    session = SessionLocal()
    try:
        # Get products without SEO tags using raw SQL
        result = session.execute(text("""
            SELECT id, name, description 
            FROM products 
            WHERE seo_tags IS NULL OR array_length(seo_tags, 1) IS NULL
            LIMIT :limit
        """), {"limit": batch_size})
        
        products_to_update = result.fetchall()
        tagged = 0
        
        for row in products_to_update:
            tags = rule_based_tags(row.name, row.description)
            if tags:
                # Update the product with tags
                session.execute(text("""
                    UPDATE products 
                    SET seo_tags = :tags 
                    WHERE id = :id
                """), {"tags": tags, "id": row.id})
                tagged += 1
        
        session.commit()
        print(f"✅ Tagged {tagged} products with SEO tags.")
        
    except Exception as e:
        session.rollback()
        print(f"❌ Error tagging products: {e}")
    finally:
        session.close()

# Optional: LLM-based tagging placeholder
def llm_based_tags(name: str, description: str = ""):
    # Implement with OpenAI or Claude if desired
    return []

if __name__ == "__main__":
    tag_unprocessed_products() 