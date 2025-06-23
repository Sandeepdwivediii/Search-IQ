import pandas as pd
import json
import os

def generate_items_csv():
    """Generate dummy items dataset"""
    items_data = [
        {"item_id": 1, "name": "Hiking Boots", "category": "Footwear"},
        {"item_id": 2, "name": "Water Bottle", "category": "Accessories"},
        {"item_id": 3, "name": "Compass", "category": "Gadgets"},
        {"item_id": 4, "name": "Energy Bar", "category": "Food"},
        {"item_id": 5, "name": "Tea Powder", "category": "Kitchen"},
        {"item_id": 6, "name": "Milk", "category": "Kitchen"},
        {"item_id": 7, "name": "Backpack", "category": "Accessories"},
        {"item_id": 8, "name": "First Aid Kit", "category": "Safety"},
        {"item_id": 9, "name": "Flashlight", "category": "Gadgets"},
        {"item_id": 10, "name": "Map", "category": "Navigation"}
    ]
    
    df = pd.DataFrame(items_data)
    df.to_csv("data/items.csv", index=False)
    print("Generated items.csv")

def generate_dependencies_json():
    """Generate dependency graph"""
    dependencies = {
        "make_tea": {
            "tea_powder": [],
            "milk": ["tea_powder"]
        },
        "go_hiking": {
            "hiking_boots": [],
            "water_bottle": [],
            "compass": ["hiking_boots"],
            "energy_bar": [],
            "backpack": [],
            "first_aid_kit": ["backpack"],
            "flashlight": [],
            "map": ["compass"]
        },
        "camping": {
            "backpack": [],
            "flashlight": [],
            "first_aid_kit": ["backpack"],
            "water_bottle": [],
            "energy_bar": []
        }
    }
    
    with open("data/dependencies.json", "w") as f:
        json.dump(dependencies, f, indent=2)
    print("Generated dependencies.json")

if __name__ == "__main__":
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    generate_items_csv()
    generate_dependencies_json()
    print("Dummy data generation complete!")