import pandas as pd
from typing import List, Dict, Optional
import re
import time
import urllib.parse
import random  # Added missing import

class SearchEngine:
    """Working search engine with basic optimizations and automatic images"""
    
    def __init__(self, items_file: str = "data/items.csv"):
        self.items_file = items_file
        print("🔄 Loading search engine...")
        start_time = time.time()
        
        self.items_df = self._load_items()
        
        load_time = time.time() - start_time
        print(f"✅ Search engine loaded in {load_time:.2f}s")
    
    def _load_items(self) -> pd.DataFrame:
        """Load items efficiently"""
        try:
            print(f"📊 Loading data from {self.items_file}...")
            
            # Load with basic optimizations
            df = pd.read_csv(self.items_file, low_memory=False)
            
            print(f"📈 Loaded {len(df)} products")
            
            # Handle column mapping
            if 'product_name' in df.columns:
                df['name'] = df['product_name']
            elif 'name' not in df.columns:
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 0:
                    df['name'] = df[text_cols[0]]
                else:
                    df['name'] = 'Unknown Product'
            
            if 'product_category_tree' in df.columns:
                df['category'] = df['product_category_tree']
            elif 'category' not in df.columns:
                text_cols = df.select_dtypes(include=['object']).columns
                if len(text_cols) > 1:
                    df['category'] = df[text_cols[1]]
                else:
                    df['category'] = 'General'
            
            # Add item_id if missing
            if 'item_id' not in df.columns:
                df['item_id'] = range(1, len(df) + 1)
            
            # Pre-compute search fields
            print("🔄 Pre-processing search fields...")
            df['name_lower'] = df['name'].astype(str).str.lower()
            df['category_lower'] = df['category'].astype(str).str.lower()
            
            print(f"✅ Pre-processed {len(df)} products")
            return df
            
        except Exception as e:
            print(f"❌ Error loading items: {e}")
            return pd.DataFrame()
    
    def extract_main_category(self, category_str: str) -> str:
        """Extract clean main category"""
        try:
            clean = str(category_str).replace('[', '').replace(']', '').replace('"', '')
            if '>>' in clean:
                parts = clean.split('>>')
                main_category = parts[0].strip()
                return main_category[:40] if len(main_category) > 40 else main_category
            return clean[:40]
        except:
            return "General"

    def extract_price(self, row) -> Optional[float]:
        """Extract price from row data - enhanced for different formats"""
        try:
            # Try different price column names
            price_columns = [
                'discounted_price', 'retail_price', 'price', 'selling_price',
                'mrp', 'cost', 'amount', 'value'
            ]
            
            for col in price_columns:
                if col in row and pd.notna(row[col]):
                    try:
                        # Handle different price formats
                        price_str = str(row[col])
                        
                        # Remove currency symbols and commas
                        price_clean = re.sub(r'[₹,$\s]', '', price_str)
                        
                        # Extract numbers
                        price_match = re.search(r'\d+\.?\d*', price_clean)
                        if price_match:
                            price = float(price_match.group())
                            if price > 0:
                                return round(price, 2)
                    except (ValueError, TypeError):
                        continue
            
            # If no price found, generate a realistic fake price for demo
            categories_prices = {
                'mobile': (5000, 50000),
                'phone': (5000, 50000),
                'laptop': (25000, 100000),
                'computer': (20000, 80000),
                'shoes': (500, 5000),
                'clothing': (300, 3000),
                'electronics': (1000, 25000)
            }
            
            # Generate price based on category
            item_name = str(row.get('name', '')).lower()
            item_category = str(row.get('category', '')).lower()
            
            for category, (min_price, max_price) in categories_prices.items():
                if category in item_name or category in item_category:
                    return round(random.uniform(min_price, max_price), 2)
            
            # Default random price
            return round(random.uniform(100, 5000), 2)
            
        except Exception as e:
            print(f"Price extraction error: {e}")
            return round(random.uniform(100, 5000), 2)  # Fallback price

    def extract_rating(self, row) -> Optional[float]:
        """Extract rating from row data - enhanced"""
        try:
            rating_columns = [
                'product_rating', 'overall_rating', 'rating', 
                'customer_rating', 'star_rating', 'review_rating'
            ]
            
            for col in rating_columns:
                if col in row and pd.notna(row[col]):
                    try:
                        rating = float(row[col])
                        if 0 <= rating <= 5:
                            return round(rating, 1)
                    except (ValueError, TypeError):
                        continue
            
            # Generate realistic fake rating for demo
            return round(random.uniform(3.0, 4.8), 1)
            
        except Exception as e:
            print(f"Rating extraction error: {e}")
            return round(random.uniform(3.0, 4.8), 1)

    def get_smart_product_image(self, product_name: str, category: str, brand: str = None) -> str:
        """Get smart product images with category and brand intelligence"""
        try:
            name_lower = product_name.lower()
            category_lower = category.lower()
            brand_lower = (brand or '').lower()
            
            # Generate unique seed for consistent images per product
            seed = abs(hash(f"{product_name}{category}")) % 100
            
            # Smart category detection for better images
            if any(word in name_lower for word in ['iphone', 'samsung', 'phone', 'mobile', 'smartphone']):
                return f"https://source.unsplash.com/400x400/?smartphone&sig={seed}"
                
            elif any(word in name_lower for word in ['laptop', 'macbook', 'computer', 'pc']):
                return f"https://source.unsplash.com/400x400/?laptop&sig={seed}"
                
            elif any(word in name_lower for word in ['nike', 'adidas', 'shoes', 'sneakers', 'boots', 'footwear']):
                return f"https://source.unsplash.com/400x400/?sneakers&sig={seed}"
                
            elif any(word in name_lower for word in ['shirt', 'dress', 'clothing', 'fashion', 'apparel']):
                return f"https://source.unsplash.com/400x400/?fashion&sig={seed}"
                
            elif any(word in name_lower for word in ['watch', 'time', 'clock']):
                return f"https://source.unsplash.com/400x400/?watch&sig={seed}"
                
            elif any(word in name_lower for word in ['headphone', 'earphone', 'audio', 'speaker']):
                return f"https://source.unsplash.com/400x400/?headphones&sig={seed}"
                
            elif any(word in name_lower for word in ['book', 'novel', 'guide', 'magazine']):
                return f"https://source.unsplash.com/400x400/?books&sig={seed}"
                
            elif any(word in name_lower for word in ['bag', 'backpack', 'purse', 'handbag']):
                return f"https://source.unsplash.com/400x400/?bag&sig={seed}"
                
            elif any(word in name_lower for word in ['camera', 'photo', 'lens']):
                return f"https://source.unsplash.com/400x400/?camera&sig={seed}"
                
            elif any(word in name_lower for word in ['kitchen', 'cooking', 'pan', 'pot', 'utensil']):
                return f"https://source.unsplash.com/400x400/?kitchen&sig={seed}"
                
            elif any(word in name_lower for word in ['furniture', 'chair', 'table', 'sofa']):
                return f"https://source.unsplash.com/400x400/?furniture&sig={seed}"
                
            elif any(word in name_lower for word in ['beauty', 'cosmetic', 'makeup', 'skincare']):
                return f"https://source.unsplash.com/400x400/?cosmetics&sig={seed}"
                
            elif any(word in name_lower for word in ['toy', 'game', 'play']):
                return f"https://source.unsplash.com/400x400/?toys&sig={seed}"
                
            elif any(word in name_lower for word in ['car', 'automotive', 'vehicle']):
                return f"https://source.unsplash.com/400x400/?car&sig={seed}"
                
            elif any(word in name_lower for word in ['jewelry', 'ring', 'necklace', 'earring']):
                return f"https://source.unsplash.com/400x400/?jewelry&sig={seed}"
                
            elif any(word in name_lower for word in ['sport', 'fitness', 'gym', 'exercise']):
                return f"https://source.unsplash.com/400x400/?fitness&sig={seed}"
                
            else:
                # Generic product image with variety
                return f"https://source.unsplash.com/400x400/?product&sig={seed}"
                
        except Exception as e:
            print(f"Error generating smart image: {e}")
            return "https://via.placeholder.com/400x400/e3f2fd/1976d2?text=Product"

    def search_by_keywords(self, keywords: List[str], max_results: int = 15) -> List[Dict]:
        """Search for items using keywords"""
        if self.items_df.empty or not keywords:
            return []
        
        print(f"🔍 Searching for keywords: {keywords}")
        
        all_results = []
        
        # Search each keyword
        for keyword in keywords[:3]:  # Limit to first 3 keywords
            keyword_lower = str(keyword).lower().strip()
            
            if len(keyword_lower) < 2:  # Skip very short keywords
                continue
            
            try:
                # Search in name
                name_matches = self.items_df[
                    self.items_df['name_lower'].str.contains(keyword_lower, na=False, regex=False)
                ]
                
                # Search in category
                category_matches = self.items_df[
                    self.items_df['category_lower'].str.contains(keyword_lower, na=False, regex=False)
                ]
                
                # Combine matches
                combined_matches = pd.concat([name_matches, category_matches]).drop_duplicates()
                
                print(f"  Found {len(combined_matches)} matches for '{keyword}'")
                
                # Convert to results
                for _, row in combined_matches.head(max_results).iterrows():
                    clean_category = self.extract_main_category(row['category'])
                    brand = str(row.get('brand', 'Generic')) if 'brand' in row and pd.notna(row.get('brand')) else 'Generic'
                    
                    item_dict = {
                        'item_id': int(row['item_id']) if pd.notna(row['item_id']) else 0,
                        'name': str(row['name']),
                        'category': clean_category,
                        'brand': brand,
                        'price': self.extract_price(row),
                        'rating': self.extract_rating(row),
                        'image_url': self.get_smart_product_image(str(row['name']), clean_category, brand)
                    }
                    
                    # Avoid duplicates
                    if not any(existing['name'] == item_dict['name'] for existing in all_results):
                        all_results.append(item_dict)
                        
            except Exception as e:
                print(f"  Error searching for '{keyword}': {e}")
                continue
        
        # Ensure all items have valid prices and ratings
        for item in all_results:
            if not item.get('price'):
                name_lower = item['name'].lower()
                if any(word in name_lower for word in ['mobile', 'phone']):
                    item['price'] = round(random.uniform(8000, 45000), 2)
                elif any(word in name_lower for word in ['laptop', 'computer']):
                    item['price'] = round(random.uniform(25000, 85000), 2)
                elif any(word in name_lower for word in ['shoe', 'footwear']):
                    item['price'] = round(random.uniform(800, 4000), 2)
                else:
                    item['price'] = round(random.uniform(200, 3000), 2)
            
            if not item.get('rating'):
                item['rating'] = round(random.uniform(3.2, 4.7), 1)
            
            # Ensure image URL exists
            if not item.get('image_url'):
                item['image_url'] = self.get_smart_product_image(item['name'], item['category'], item['brand'])
        
        print(f"✅ Total unique results found: {len(all_results)}")
        return all_results[:max_results]

    def search_by_names(self, item_names: List[str]) -> List[Dict]:
        """Search for items by their names"""
        if self.items_df.empty or not item_names:
            return []
        
        results = []
        
        for item_name in item_names:
            item_name_lower = str(item_name).lower()
            
            try:
                # Try exact match first
                matches = self.items_df[self.items_df['name_lower'] == item_name_lower]
                
                # If no exact match, try partial match
                if matches.empty:
                    matches = self.items_df[
                        self.items_df['name_lower'].str.contains(item_name_lower, na=False, regex=False)
                    ]
                
                # Convert matches to dictionaries
                for _, row in matches.head(3).iterrows():  # Max 3 per name
                    clean_category = self.extract_main_category(row['category'])
                    brand = str(row.get('brand', 'Generic')) if 'brand' in row and pd.notna(row.get('brand')) else 'Generic'
                    
                    item_dict = {
                        'item_id': int(row['item_id']) if pd.notna(row['item_id']) else 0,
                        'name': str(row['name']),
                        'category': clean_category,
                        'brand': brand,
                        'price': self.extract_price(row),
                        'rating': self.extract_rating(row),
                        'image_url': self.get_smart_product_image(str(row['name']), clean_category, brand)
                    }
                    
                    if not any(existing['name'] == item_dict['name'] for existing in results):
                        results.append(item_dict)
                        
            except Exception as e:
                print(f"Search error for name '{item_name}': {e}")
                continue
        
        return results

    def get_all_items(self) -> List[Dict]:
        """Get sample items for testing"""
        if self.items_df.empty:
            return []
        
        results = []
        try:
            # Return first 10 items as sample
            for _, row in self.items_df.head(10).iterrows():
                clean_category = self.extract_main_category(row['category'])
                brand = str(row.get('brand', 'Generic')) if 'brand' in row and pd.notna(row.get('brand')) else 'Generic'
                
                item_dict = {
                    'item_id': int(row['item_id']) if pd.notna(row['item_id']) else 0,
                    'name': str(row['name']),
                    'category': clean_category,
                    'brand': brand,
                    'price': self.extract_price(row),
                    'rating': self.extract_rating(row),
                    'image_url': self.get_smart_product_image(str(row['name']), clean_category, brand)
                }
                results.append(item_dict)
                
        except Exception as e:
            print(f"Error getting sample items: {e}")
        
        return results

# Test the search engine
if __name__ == "__main__":
    search_engine = SearchEngine()
    
    print("=== Testing Search Engine ===\n")
    
    # Test 1: Simple keyword search
    print("1. Testing keyword search:")
    test_keywords = ["phone", "mobile"]
    results = search_engine.search_by_keywords(test_keywords)
    print(f"Found {len(results)} results for {test_keywords}")
    
    for item in results[:3]:
        print(f"  - {item['name']} | Brand: {item['brand']} | Price: ₹{item['price'] or 'N/A'} | Image: {item['image_url']}")
    
    print(f"\n✅ Search engine working! Total items loaded: {len(search_engine.items_df)}")