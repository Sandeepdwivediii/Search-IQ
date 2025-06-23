import pandas as pd
import sys
import os
from typing import List, Dict, Optional

# ─── CONFIGURATION ───────────────────────────────────────────────────
DATA_DIR = "data"
ORDERS_CSV = os.path.join(DATA_DIR, "xyz_user_orders.csv")
SPARES_CSV = os.path.join(DATA_DIR, "xyz_spares.csv")
SAMSUNG_ORDERS_CSV = os.path.join(DATA_DIR, "samsung_user_orders.csv")
SAMSUNG_SPARES_CSV = os.path.join(DATA_DIR, "samsung_ac_parts_final.csv")

class SparePartRecommender:
    def __init__(self):
        """Initialize the recommender with data loading"""
        self.orders_data = {}
        self.spares_data = {}
        self._load_data()
    
    def _load_data(self):
        """Load all CSV data files"""
        try:
            # Load XYZ data
            if os.path.exists(ORDERS_CSV):
                self.orders_data['xyz'] = pd.read_csv(ORDERS_CSV)
            if os.path.exists(SPARES_CSV):
                xyz_spares = pd.read_csv(SPARES_CSV)
                xyz_spares['compatible_models'] = xyz_spares['compatible_models'].fillna("")
                self.spares_data['xyz'] = xyz_spares
            
            # Load Samsung data
            if os.path.exists(SAMSUNG_ORDERS_CSV):
                self.orders_data['samsung'] = pd.read_csv(SAMSUNG_ORDERS_CSV)
            if os.path.exists(SAMSUNG_SPARES_CSV):
                samsung_spares = pd.read_csv(SAMSUNG_SPARES_CSV)
                # Ensure compatible_models column exists
                if 'compatible_models' not in samsung_spares.columns:
                    samsung_spares['compatible_models'] = ""
                samsung_spares['compatible_models'] = samsung_spares['compatible_models'].fillna("")
                self.spares_data['samsung'] = samsung_spares
            
            print(f"✅ Loaded spare parts data for brands: {list(self.spares_data.keys())}")
            
        except Exception as e:
            print(f"❌ Error loading spare parts data: {e}")
            # Initialize with empty data to prevent crashes
            self.orders_data = {'xyz': pd.DataFrame(), 'samsung': pd.DataFrame()}
            self.spares_data = {'xyz': pd.DataFrame(), 'samsung': pd.DataFrame()}
    
    def get_supported_brands(self) -> List[str]:
        """Return list of supported brands"""
        return list(self.spares_data.keys())
    
    def get_device_models(self, brand: str) -> List[str]:
        """Get available device models for a brand"""
        brand = brand.lower()
        if brand in self.orders_data and not self.orders_data[brand].empty:
            if 'product_model' in self.orders_data[brand].columns:
                return self.orders_data[brand]['product_model'].unique().tolist()
        return []
    
    def get_recommendations(self, device_model: str, issue_description: str, 
                          brand: str = "samsung", max_results: int = 10) -> List[Dict]:
        """
        Get spare part recommendations based on device model and issue description
        """
        brand = brand.lower()
        
        if brand not in self.spares_data or self.spares_data[brand].empty:
            return []
        
        spares_df = self.spares_data[brand].copy()
        
        # Score each spare part
        recommendations = []
        
        for _, row in spares_df.iterrows():
            score = self._calculate_compatibility_score(row, device_model, issue_description)
            
            if score > 0:  # Only include parts with some relevance
                rec = {
                    "part_name": str(row.get('part_name', 'Unknown Part')),
                    "part_number": str(row.get('part_number', 'N/A')),
                    "price": float(row.get('price_usd', row.get('price', 0))),
                    "availability": self._get_availability_status(row),
                    "compatibility_score": score,
                    "description": str(row.get('description', '')),
                    "image_url": self._generate_part_image_url(row),
                    "brand": brand,
                    "category": str(row.get('category', ''))
                }
                recommendations.append(rec)
        
        # Sort by compatibility score and return top results
        recommendations.sort(key=lambda x: x['compatibility_score'], reverse=True)
        return recommendations[:max_results]
    
    def _calculate_compatibility_score(self, part_row, device_model: str, issue_description: str) -> float:
        """Calculate compatibility score for a spare part"""
        score = 0.0
        
        # Model compatibility (highest weight)
        if 'compatible_models' in part_row and device_model.upper() in str(part_row['compatible_models']).upper():
            score += 0.4
        
        # Keyword matching in part name (medium weight)
        part_name = str(part_row.get('part_name', '')).lower()
        issue_words = issue_description.lower().split()
        
        for word in issue_words:
            if len(word) > 3 and word in part_name:  # Skip short words
                score += 0.1
        
        # Category/type matching (medium weight)
        category = str(part_row.get('category', '')).lower()
        if any(word in category for word in issue_words if len(word) > 3):
            score += 0.2
        
        # Common issue keywords (specific matching)
        issue_keywords = {
            'cooling': ['compressor', 'refrigerant', 'condenser', 'evaporator'],
            'noise': ['fan', 'motor', 'bearing', 'compressor'],
            'leak': ['seal', 'gasket', 'drain', 'valve'],
            'remote': ['remote', 'control', 'receiver', 'sensor'],
            'display': ['display', 'panel', 'led', 'screen']
        }
        
        for issue_type, keywords in issue_keywords.items():
            if issue_type in issue_description.lower():
                for keyword in keywords:
                    if keyword in part_name:
                        score += 0.15
        
        # Base relevance for any AC part
        if score == 0 and any(word in part_name for word in ['ac', 'air', 'conditioner']):
            score = 0.1
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _get_availability_status(self, part_row) -> str:
        """Get availability status for a part"""
        # You can customize this based on your data
        if 'availability' in part_row:
            return str(part_row['availability'])
        elif 'stock' in part_row:
            stock = part_row['stock']
            if stock > 10:
                return "In Stock"
            elif stock > 0:
                return "Limited Stock"
            else:
                return "Out of Stock"
        else:
            return "Available"
    
    def _generate_part_image_url(self, part_row) -> str:
        """Generate or get image URL for a part"""
        if 'image_url' in part_row and pd.notna(part_row['image_url']):
            return str(part_row['image_url'])
        
        # Generate placeholder image based on part name
        part_name = str(part_row.get('part_name', 'spare-part'))
        seed = abs(hash(part_name)) % 100
        return f"https://source.unsplash.com/300x300/?electronics,parts&sig={seed}"

# ─── LEGACY FUNCTION FOR BACKWARD COMPATIBILITY ─────────────────────
def recommend_spare_parts(invoice_number: str, fault_keyword: str, top_n: int = 3):
    """
    Legacy function - given an invoice number and a faulty-part keyword,
    returns a DataFrame of up to top_n recommended spare parts.
    """
    # Load data directly (for standalone usage)
    if not os.path.exists(ORDERS_CSV) or not os.path.exists(SPARES_CSV):
        raise ValueError("Required CSV files not found in data directory")
    
    orders_df = pd.read_csv(ORDERS_CSV)
    spares_df = pd.read_csv(SPARES_CSV)
    spares_df['compatible_models'] = spares_df['compatible_models'].fillna("")
    
    # 1. Lookup order
    order = orders_df.loc[orders_df['invoice_number'] == invoice_number]
    if order.empty:
        raise ValueError(f"No order found for invoice '{invoice_number}'")

    category = order.iloc[0]['category']
    user_model = order.iloc[0]['product_model']
    user_company = order.iloc[0]['company']

    # 2. Filter by category
    candidates = spares_df[spares_df['category'].str.lower() == category.lower()].copy()

    # 3. Score each candidate
    def score_row(row):
        model_match = 1 if user_model in row['compatible_models'] else 0
        keyword_match = 1 if fault_keyword.lower() in row['part_name'].lower() else 0
        company_match = 1 if row.get('company', '').lower() == user_company.lower() else 0
        price_score = -row['price_usd']  # prefer cheaper
        return (model_match + company_match, keyword_match, price_score)

    candidates['score'] = candidates.apply(score_row, axis=1)

    # 4. Sort and return top_n
    ranked = candidates.sort_values('score', ascending=False)
    return ranked.head(top_n)[[
        'part_name',
        'part_number',
        'company',
        'price_usd',
        'compatible_models',
        'product_url'
    ]]

# ─── MAIN SCRIPT ─────────────────────────────────────────────────────
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python spare_part_recommender_model.py <INVOICE_NUMBER> <FAULT_KEYWORD>")
        sys.exit(1)

    invoice = sys.argv[1]
    keyword = sys.argv[2]

    try:
        results = recommend_spare_parts(invoice, keyword)
        print(f"\nTop {len(results)} recommendations for invoice '{invoice}', fault '{keyword}':")
        print(results.to_string(index=False))
    except ValueError as e:
        print(f"Error: {e}")