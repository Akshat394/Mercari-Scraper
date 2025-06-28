import pytest
from core.product_ranker import ProductRanker

class TestProductRanker:
    """Test suite for ProductRanker"""
    
    @pytest.fixture
    def ranker(self):
        """Create ProductRanker instance for testing"""
        return ProductRanker()
    
    @pytest.fixture
    def sample_products(self):
        """Sample product data for testing"""
        return [
            {
                "id": "1",
                "name": "iPhone 15 Pro",
                "price": 150000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics",
                "brand": "Apple"
            },
            {
                "id": "2",
                "name": "iPhone 14",
                "price": 120000,
                "condition": "like_new",
                "seller_rating": 4.5,
                "category": "Electronics",
                "brand": "Apple"
            },
            {
                "id": "3",
                "name": "Samsung Galaxy S24",
                "price": 140000,
                "condition": "new",
                "seller_rating": 4.2,
                "category": "Electronics",
                "brand": "Samsung"
            },
            {
                "id": "4",
                "name": "Nike Shoes",
                "price": 8000,
                "condition": "good",
                "seller_rating": 4.0,
                "category": "Fashion",
                "brand": "Nike"
            }
        ]
    
    def test_ranker_initialization(self, ranker):
        """Test ProductRanker initializes correctly"""
        assert ranker is not None
    
    def test_rank_products_basic(self, ranker, sample_products):
        """Test basic product ranking without preferences"""
        result = ranker.rank_products(sample_products, {})
        
        assert len(result) == len(sample_products)
        assert all(isinstance(product, dict) for product in result)
        # Should maintain all products
        product_ids = [p["id"] for p in result]
        assert "1" in product_ids
        assert "2" in product_ids
        assert "3" in product_ids
        assert "4" in product_ids
    
    def test_rank_products_with_category_preference(self, ranker, sample_products):
        """Test ranking with category preference"""
        preferences = {"category": "Electronics"}
        
        result = ranker.rank_products(sample_products, preferences)
        
        # Electronics should be ranked higher
        electronics_products = [p for p in result if p["category"] == "Electronics"]
        fashion_products = [p for p in result if p["category"] == "Fashion"]
        
        # All electronics should come before fashion
        electronics_indices = [i for i, p in enumerate(result) if p["category"] == "Electronics"]
        fashion_indices = [i for i, p in enumerate(result) if p["category"] == "Fashion"]
        
        assert all(e < f for e in electronics_indices for f in fashion_indices)
    
    def test_rank_products_with_brand_preference(self, ranker, sample_products):
        """Test ranking with brand preference"""
        preferences = {"brand": "Apple"}
        
        result = ranker.rank_products(sample_products, preferences)
        
        # Apple products should be ranked higher
        apple_products = [p for p in result if p["brand"] == "Apple"]
        non_apple_products = [p for p in result if p["brand"] != "Apple"]
        
        # All Apple products should come before non-Apple
        apple_indices = [i for i, p in enumerate(result) if p["brand"] == "Apple"]
        non_apple_indices = [i for i, p in enumerate(result) if p["brand"] != "Apple"]
        
        assert all(a < n for a in apple_indices for n in non_apple_indices)
    
    def test_rank_products_with_price_range(self, ranker, sample_products):
        """Test ranking with price range preference"""
        preferences = {"price_range": {"min": 100000, "max": 160000}}
        
        result = ranker.rank_products(sample_products, preferences)
        
        # Products within price range should be ranked higher
        within_range = [p for p in result if 100000 <= p["price"] <= 160000]
        outside_range = [p for p in result if not (100000 <= p["price"] <= 160000)]
        
        if within_range and outside_range:
            within_indices = [i for i, p in enumerate(result) if 100000 <= p["price"] <= 160000]
            outside_indices = [i for i, p in enumerate(result) if not (100000 <= p["price"] <= 160000)]
            
            assert all(w < o for w in within_indices for o in outside_indices)
    
    def test_rank_products_with_condition_preference(self, ranker, sample_products):
        """Test ranking with condition preference"""
        preferences = {"condition": "new"}
        
        result = ranker.rank_products(sample_products, preferences)
        
        # New condition products should be ranked higher
        new_products = [p for p in result if p["condition"] == "new"]
        other_products = [p for p in result if p["condition"] != "new"]
        
        if new_products and other_products:
            new_indices = [i for i, p in enumerate(result) if p["condition"] == "new"]
            other_indices = [i for i, p in enumerate(result) if p["condition"] != "new"]
            
            assert all(n < o for n in new_indices for o in other_indices)
    
    def test_rank_products_with_multiple_preferences(self, ranker, sample_products):
        """Test ranking with multiple preferences"""
        preferences = {
            "category": "Electronics",
            "brand": "Apple",
            "condition": "new"
        }
        
        result = ranker.rank_products(sample_products, preferences)
        
        # iPhone 15 Pro should be ranked first (matches all preferences)
        assert result[0]["id"] == "1"
        assert result[0]["name"] == "iPhone 15 Pro"
    
    def test_rank_products_empty_list(self, ranker):
        """Test ranking with empty product list"""
        result = ranker.rank_products([], {})
        
        assert result == []
    
    def test_rank_products_single_product(self, ranker, sample_products):
        """Test ranking with single product"""
        single_product = [sample_products[0]]
        
        result = ranker.rank_products(single_product, {})
        
        assert len(result) == 1
        assert result[0]["id"] == "1"
    
    def test_rank_products_duplicate_removal(self, ranker, sample_products):
        """Test that duplicate products are removed"""
        # Add duplicate product
        products_with_duplicate = sample_products + [sample_products[0]]
        
        result = ranker.rank_products(products_with_duplicate, {})
        
        # Should have no duplicates
        product_ids = [p["id"] for p in result]
        assert len(product_ids) == len(set(product_ids))
        assert len(result) == len(sample_products)
    
    def test_rank_products_price_optimization(self, ranker, sample_products):
        """Test that price optimization works correctly"""
        preferences = {"price_range": {"min": 100000, "max": 200000}}
        
        result = ranker.rank_products(sample_products, preferences)
        
        # Products within price range should be ranked by price (lower first)
        within_range = [p for p in result if 100000 <= p["price"] <= 200000]
        if len(within_range) > 1:
            prices = [p["price"] for p in within_range]
            assert prices == sorted(prices)
    
    def test_rank_products_rating_consideration(self, ranker, sample_products):
        """Test that seller rating is considered in ranking"""
        # Create products with same category but different ratings
        test_products = [
            {
                "id": "high_rating",
                "name": "High Rating Product",
                "price": 100000,
                "condition": "new",
                "seller_rating": 5.0,
                "category": "Electronics",
                "brand": "Test"
            },
            {
                "id": "low_rating",
                "name": "Low Rating Product", 
                "price": 100000,
                "condition": "new",
                "seller_rating": 3.0,
                "category": "Electronics",
                "brand": "Test"
            }
        ]
        
        result = ranker.rank_products(test_products, {"category": "Electronics"})
        
        # Higher rating should be ranked first
        assert result[0]["seller_rating"] > result[1]["seller_rating"]
    
    def test_rank_products_complex_scenario(self, ranker):
        """Test complex ranking scenario with multiple factors"""
        complex_products = [
            {
                "id": "perfect_match",
                "name": "Perfect Match",
                "price": 120000,
                "condition": "new",
                "seller_rating": 4.8,
                "category": "Electronics",
                "brand": "Apple"
            },
            {
                "id": "good_match",
                "name": "Good Match",
                "price": 110000,
                "condition": "like_new", 
                "seller_rating": 4.5,
                "category": "Electronics",
                "brand": "Apple"
            },
            {
                "id": "partial_match",
                "name": "Partial Match",
                "price": 130000,
                "condition": "new",
                "seller_rating": 4.2,
                "category": "Electronics",
                "brand": "Samsung"
            },
            {
                "id": "no_match",
                "name": "No Match",
                "price": 8000,
                "condition": "good",
                "seller_rating": 4.0,
                "category": "Fashion",
                "brand": "Nike"
            }
        ]
        
        preferences = {
            "category": "Electronics",
            "brand": "Apple",
            "condition": "new",
            "price_range": {"min": 100000, "max": 150000}
        }
        
        result = ranker.rank_products(complex_products, preferences)
        
        # Perfect match should be first
        assert result[0]["id"] == "perfect_match"
        
        # Good match should be second
        assert result[1]["id"] == "good_match"
        
        # Partial match should be third
        assert result[2]["id"] == "partial_match"
        
        # No match should be last
        assert result[3]["id"] == "no_match" 