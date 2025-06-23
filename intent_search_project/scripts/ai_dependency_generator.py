import pandas as pd
import json
import re
from collections import defaultdict

class AISmartDependencyGenerator:
    def __init__(self):
        print("🤖 Loading AI-powered dependency generator (fixed version)...")
        
        # AI-like logic using pattern matching and semantic understanding
        self.product_intelligence = {
            "fashion_shopping": {
                "foundation_layer": ["bra", "underwear", "brief", "innerwear", "undergarment", "panty"],
                "clothing_layer": ["shirt", "top", "kurta", "dress", "blouse", "pant", "jean", "trouser"],
                "footwear_layer": ["shoe", "sandal", "slipper", "boot", "sneaker"],
                "accessory_layer": ["bag", "handbag", "watch", "jewelry", "belt", "sunglass"]
            },
            "tech_shopping": {
                "power_layer": ["charger", "cable", "adapter", "power", "battery"],
                "device_layer": ["phone", "mobile", "laptop", "computer", "tablet"],
                "protection_layer": ["case", "cover", "protector", "screen"],
                "accessory_layer": ["headphone", "speaker", "mouse", "keyboard"]
            },
            "home_shopping": {
                "furniture_layer": ["bed", "sofa", "chair", "table", "wardrobe"],
                "appliance_layer": ["fan", "ac", "light", "lamp"],
                "comfort_layer": ["mattress", "pillow", "sheet", "cushion"],
                "decor_layer": ["curtain", "decoration", "frame", "plant"]
            }
        }
        
        print("✅ AI intelligence patterns loaded")

    def generate_ai_dependencies(self):
        """Generate smart dependencies using AI-like reasoning"""
        
        print("📊 Loading data...")
        df = pd.read_csv('data/items.csv')
        print(f"Loaded {len(df)} products")
        
        # AI-like product analysis
        print("🧠 AI analyzing products...")
        smart_groups = self.ai_smart_grouping(df)
        
        # AI dependency creation
        print("⚡ Creating intelligent dependencies...")
        dependencies = self.create_intelligent_dependencies(smart_groups)
        
        # Save
        with open('data/dependencies.json', 'w') as f:
            json.dump(dependencies, f, indent=2)
        
        print("✅ AI dependencies created!")
        self.show_intelligent_summary(dependencies)
        
        return dependencies

    def ai_smart_grouping(self, df):
        """AI-like intelligent grouping of products"""
        
        smart_groups = defaultdict(list)
        
        for _, row in df.iterrows():
            product_name = str(row['product_name']).lower()
            category = str(row['product_category_tree']).lower()
            combined_text = f"{product_name} {category}"
            
            # AI-like intent detection
            intent = self.detect_intent_intelligently(combined_text)
            
            # AI-like product understanding
            product_info = {
                'name': str(row['product_name']),
                'category': str(row['product_category_tree']),
                'text': combined_text,
                'layer': self.determine_product_layer(combined_text, intent),
                'intelligence_score': self.calculate_intelligence_score(combined_text, intent)
            }
            
            smart_groups[intent].append(product_info)
        
        return dict(smart_groups)

    def detect_intent_intelligently(self, text):
        """Intelligent intent detection using multiple signals"""
        
        # Multi-signal analysis (AI-like)
        signals = {
            "fashion_shopping": 0,
            "tech_shopping": 0,
            "home_shopping": 0,
            "general_shopping": 0
        }
        
        # Fashion signals
        fashion_indicators = [
            'clothing', 'apparel', 'fashion', 'wear', 'dress', 'shirt', 'pant',
            'footwear', 'shoe', 'bag', 'jewelry', 'watch', 'bra', 'brief'
        ]
        signals["fashion_shopping"] = sum(1 for word in fashion_indicators if word in text)
        
        # Tech signals
        tech_indicators = [
            'electronics', 'mobile', 'phone', 'computer', 'laptop', 'device',
            'charger', 'cable', 'case', 'headphone', 'speaker'
        ]
        signals["tech_shopping"] = sum(1 for word in tech_indicators if word in text)
        
        # Home signals
        home_indicators = [
            'home', 'furniture', 'kitchen', 'bed', 'sofa', 'table', 'chair',
            'lamp', 'light', 'curtain', 'cushion', 'decor'
        ]
        signals["home_shopping"] = sum(1 for word in home_indicators if word in text)
        
        # Return strongest signal
        if max(signals.values()) == 0:
            return "general_shopping"
        
        return max(signals, key=signals.get)

    def determine_product_layer(self, text, intent):
        """Determine which logical layer a product belongs to"""
        
        if intent not in self.product_intelligence:
            return "main_layer"
        
        layers = self.product_intelligence[intent]
        
        # Check each layer
        for layer_name, keywords in layers.items():
            if any(keyword in text for keyword in keywords):
                return layer_name
        
        return "main_layer"

    def calculate_intelligence_score(self, text, intent):
        """Calculate how well we understand this product"""
        
        score = 0
        
        # More keywords = better understanding
        word_count = len(text.split())
        score += min(word_count, 10)  # Cap at 10
        
        # Known patterns = higher score
        if intent != "general_shopping":
            score += 5
        
        # Specific layer detection = higher score
        layer = self.determine_product_layer(text, intent)
        if layer != "main_layer":
            score += 3
        
        return score

    def create_intelligent_dependencies(self, smart_groups):
        """Create dependencies using intelligent reasoning"""
        
        dependencies = {}
        
        for intent, products in smart_groups.items():
            if len(products) == 0:
                continue
            
            print(f"  🧠 Intelligent processing: {intent} ({len(products)} products)")
            
            # Group by layer for intelligent ordering
            layer_groups = defaultdict(list)
            for product in products:
                layer_groups[product['layer']].append(product)
            
            # Intelligent layer ordering
            layer_order = self.get_intelligent_layer_order(intent)
            
            # Create intelligent dependency chain
            dependencies[intent] = self.create_intelligent_chain(layer_groups, layer_order)
        
        return dependencies

    def get_intelligent_layer_order(self, intent):
        """Get the intelligent order of layers for each intent"""
        
        layer_orders = {
            "fashion_shopping": ["foundation_layer", "clothing_layer", "footwear_layer", "accessory_layer"],
            "tech_shopping": ["power_layer", "device_layer", "protection_layer", "accessory_layer"],
            "home_shopping": ["furniture_layer", "appliance_layer", "comfort_layer", "decor_layer"]
        }
        
        return layer_orders.get(intent, ["main_layer"])

    def create_intelligent_chain(self, layer_groups, layer_order):
        """Create an intelligent dependency chain"""
        
        dependencies = {}
        previous_item = None
        
        for layer in layer_order:
            if layer in layer_groups and layer_groups[layer]:
                # Sort by intelligence score
                sorted_products = sorted(layer_groups[layer], 
                                       key=lambda x: x['intelligence_score'], 
                                       reverse=True)
                
                # Take the most intelligent product from this layer
                product = sorted_products[0]
                product_key = self.clean_name(product['name'])
                
                if previous_item is None:
                    dependencies[product_key] = []
                else:
                    dependencies[product_key] = [previous_item]
                
                previous_item = product_key
        
        # Add a few more products if available
        all_products = []
        for products in layer_groups.values():
            all_products.extend(products)
        
        # Sort all by intelligence and add top ones not yet included
        all_sorted = sorted(all_products, key=lambda x: x['intelligence_score'], reverse=True)
        added_count = len(dependencies)
        
        for product in all_sorted:
            if added_count >= 5:  # Limit to 5 products per intent
                break
            
            product_key = self.clean_name(product['name'])
            if product_key not in dependencies:
                if previous_item is None:
                    dependencies[product_key] = []
                else:
                    dependencies[product_key] = [previous_item]
                
                previous_item = product_key
                added_count += 1
        
        return dependencies

    def clean_name(self, name):
        """Clean product name for keys"""
        cleaned = re.sub(r'[^\w\s-]', '', str(name).lower())
        cleaned = re.sub(r'\s+', '_', cleaned.strip())
        return cleaned[:30]

    def show_intelligent_summary(self, dependencies):
        """Show intelligent analysis summary"""
        
        print("\n🤖 AI INTELLIGENT DEPENDENCY ANALYSIS:")
        print("=" * 60)
        
        explanations = {
            "fashion_shopping": "Foundation → Clothing → Footwear → Accessories",
            "tech_shopping": "Power → Devices → Protection → Accessories",
            "home_shopping": "Furniture → Appliances → Comfort → Decor"
        }
        
        for intent, deps in dependencies.items():
            print(f"\n🛍️ {intent.upper()}:")
            print(f"   Logic: {explanations.get(intent, 'Intelligent ordering')}")
            print(f"   Products: {len(deps)} intelligently ordered")
            
            if deps:
                chain = self.build_dependency_chain(deps)
                for i, item in enumerate(chain, 1):
                    readable = item.replace('_', ' ').title()[:50]
                    if i == 1:
                        print(f"     {i}. {readable} ← AI START")
                    else:
                        print(f"     {i}. {readable}")

    def build_dependency_chain(self, deps):
        """Build the dependency chain"""
        # Find start
        start = None
        for item, deps_list in deps.items():
            if not deps_list:
                start = item
                break
        
        if not start:
            return list(deps.keys())
        
        # Build chain
        chain = [start]
        while True:
            current = chain[-1]
            next_item = None
            
            for item, deps_list in deps.items():
                if item not in chain and current in deps_list:
                    next_item = item
                    break
            
            if next_item:
                chain.append(next_item)
            else:
                break
        
        return chain

def generate_ai_dependencies():
    """Main function"""
    generator = AISmartDependencyGenerator()
    return generator.generate_ai_dependencies()

if __name__ == "__main__":
    generate_ai_dependencies()