# FastAPI router for search endpoints with caching and theme




from fastapi import APIRouter, HTTPException
from app.models.request_models import SearchRequest
from app.models.response_models import SearchResponse, Item
from app.services.search_engine import SearchEngine
import time
from functools import lru_cache
import hashlib

router = APIRouter()

# Initialize search engine
search_engine = SearchEngine()

# Simple in-memory cache
search_cache = {}
theme_cache = {}
MAX_CACHE_SIZE = 200  # Limit cache size

# Activity themes (cached for performance)
ACTIVITY_THEMES = {
    "hiking": {
        "keywords": ["hiking", "hike", "trek", "mountain", "trail", "outdoor", "adventure", "walking"],
        "related_items": ["boots", "shoes", "backpack", "bag", "water", "bottle", "compass", "map", 
                         "energy", "snack", "flashlight", "torch", "jacket", "gear", "equipment"]
    },
    "camping": {
        "keywords": ["camping", "camp", "tent", "campfire", "outdoor", "nature"],
        "related_items": ["tent", "sleeping", "bag", "stove", "cooking", "lantern", "flashlight", 
                         "chair", "table", "cooler", "fire", "rope", "tarp"]
    },
    "cooking": {
        "keywords": ["cooking", "cook", "kitchen", "food", "recipe", "meal", "tea", "coffee"],
        "related_items": ["pan", "pot", "knife", "spoon", "plate", "cup", "mug", "stove", 
                         "mixer", "blender", "oil", "spice", "ingredient"]
    },
    "fitness": {
        "keywords": ["fitness", "gym", "exercise", "workout", "sport", "training", "yoga"],
        "related_items": ["dumbbell", "weight", "mat", "shoes", "clothes", "bottle", "towel", 
                         "tracker", "band", "equipment"]
    },
    "tech": {
        "keywords": ["technology", "tech", "electronics", "gadget", "computer", "phone", "mobile"],
        "related_items": ["charger", "cable", "case", "screen", "headphone", "speaker", "mouse", 
                         "keyboard", "adapter", "battery", "memory", "storage"]
    },
    "fashion": {
        "keywords": ["fashion", "clothing", "wear", "dress", "style", "outfit"],
        "related_items": ["shirt", "pant", "dress", "shoe", "bag", "belt", "watch", "jewelry", 
                         "sunglass", "hat", "scarf"]
    }
}

def create_cache_key(query: str, max_results: int = 15) -> str:
    """Create a cache key for the query"""
    combined = f"{query.lower().strip()}:{max_results}"
    return hashlib.md5(combined.encode()).hexdigest()

def clean_cache():
    """Clean cache if it gets too large"""
    global search_cache, theme_cache
    if len(search_cache) > MAX_CACHE_SIZE:
        # Remove oldest entries (simple FIFO)
        keys_to_remove = list(search_cache.keys())[:50]
        for key in keys_to_remove:
            del search_cache[key]
        print(f"🧹 Cache cleaned, removed {len(keys_to_remove)} entries")

@lru_cache(maxsize=500)
def detect_activity_theme_cached(query: str) -> str:
    """Cached theme detection - super fast repeated calls"""
    query_lower = query.lower()
    
    for theme, config in ACTIVITY_THEMES.items():
        for keyword in config["keywords"]:
            if keyword in query_lower:
                return theme
    
    return None

def search_by_theme_optimized(theme: str, original_query: str, max_results: int = 15) -> list:
    """Optimized theme-based search"""
    
    # Check theme cache first
    theme_cache_key = f"{theme}:{max_results}"
    if theme_cache_key in theme_cache:
        print("⚡ Theme cache hit!")
        return theme_cache[theme_cache_key]
    
    if theme not in ACTIVITY_THEMES:
        return []
    
    # Get theme configuration
    theme_config = ACTIVITY_THEMES[theme]
    
    # Use only most relevant keywords for performance
    priority_keywords = theme_config["keywords"][:3] + theme_config["related_items"][:10]
    
    # Fast search with limited keywords
    theme_results = search_engine.search_by_keywords(priority_keywords, max_results * 2)
    
    # Quick scoring and ranking
    scored_results = []
    original_words = original_query.lower().split()
    
    for item in theme_results:
        score = calculate_theme_relevance_fast(item, theme_config, original_words)
        if score > 0:
            item['relevance_score'] = score
            scored_results.append(item)
    
    # Sort by relevance score (faster than complex sorting)
    scored_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
    
    # Clean up and prepare results
    final_results = []
    for item in scored_results[:max_results]:
        if 'relevance_score' in item:
            del item['relevance_score']
        final_results.append(item)
    
    # Cache theme results
    theme_cache[theme_cache_key] = final_results
    
    return final_results

def calculate_theme_relevance_fast(item: dict, theme_config: dict, original_words: list) -> int:
    """Fast relevance calculation"""
    score = 0
    item_text = f"{item['name']} {item['category']}".lower()
    
    # Quick scoring - only check first few keywords
    for keyword in theme_config["keywords"][:2]:
        if keyword in item_text:
            score += 5
    
    for keyword in theme_config["related_items"][:5]:
        if keyword in item_text:
            score += 2
    
    # Bonus for original query words
    for word in original_words:
        if len(word) > 2 and word in item_text:
            score += 3
    
    return score

@router.post("/search", response_model=SearchResponse)
async def search_items_cached(request: SearchRequest):
    """
    Cached search endpoint - 0.1-0.5 second response time
    """
    start_time = time.time()
    
    try:
        # Clean query
        query = str(request.query).strip()
        if not query:
            return SearchResponse(items=[], intent=None, total_results=0)
        
        # Create cache key
        cache_key = create_cache_key(query, 15)
        
        # Check cache first (fastest path)
        if cache_key in search_cache:
            cached_result = search_cache[cache_key]
            print(f"⚡ CACHE HIT! Search took {(time.time() - start_time)*1000:.1f}ms")
            return cached_result
        
        print(f"🔍 Cache miss, performing search...")
        
        # Detect theme (cached function)
        detected_theme = detect_activity_theme_cached(query.lower())
        
        if detected_theme:
            # Theme-based search (optimized)
            items_data = search_by_theme_optimized(detected_theme, query, 15)
        else:
            # Fallback to keyword search (limit keywords for speed)
            keywords = query.split()[:3]  # Only use first 3 words
            items_data = search_engine.search_by_keywords(keywords, max_results=15)
        
        # Convert to response format
        items = [Item(**item_data) for item_data in items_data]
        
        # Create response
        result = SearchResponse(
            items=items,
            intent=detected_theme,
            total_results=len(items)
        )
        
        # Cache the result
        search_cache[cache_key] = result
        
        # Clean cache if needed
        if len(search_cache) > MAX_CACHE_SIZE:
            clean_cache()
        
        search_time = (time.time() - start_time) * 1000
        print(f"🚀 Search completed in {search_time:.1f}ms")
        
        return result
        
    except Exception as e:
        print(f"❌ Search error: {e}")
        return SearchResponse(items=[], intent=None, total_results=0)

@router.get("/test")
async def test_endpoint():
    """Test endpoint"""
    return {"message": "Cached Search API is working!", "status": "ok"}

@router.get("/cache-stats")
async def cache_stats():
    """Get cache statistics"""
    return {
        "search_cache_size": len(search_cache),
        "theme_cache_size": len(theme_cache),
        "max_cache_size": MAX_CACHE_SIZE,
        "cached_themes": list(theme_cache.keys())
    }

@router.post("/clear-cache")
async def clear_cache():
    """Clear all caches"""
    global search_cache, theme_cache
    search_cache.clear()
    theme_cache.clear()
    detect_activity_theme_cached.cache_clear()
    return {"message": "All caches cleared successfully"}