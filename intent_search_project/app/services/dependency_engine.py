import json
import networkx as nx
from typing import List, Dict, Optional

class DependencyEngine:
    """Handles dependency relationships and topological sorting"""
    
    def __init__(self, dependencies_file: str = "data/dependencies.json"):
        self.dependencies_file = dependencies_file
        self.dependencies = self._load_dependencies()
    
    def _load_dependencies(self) -> Dict:
        """Load dependencies from JSON file"""
        try:
            with open(self.dependencies_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Dependencies file {self.dependencies_file} not found")
            return {}
        except json.JSONDecodeError:
            print(f"Error parsing {self.dependencies_file}")
            return {}
    
    def get_items_for_intent(self, intent: str) -> List[str]:
        """Get all items needed for a given intent"""
        if intent not in self.dependencies:
            return []
        
        return list(self.dependencies[intent].keys())
    
    def sort_items_by_dependencies(self, intent: str) -> List[str]:
        """
        Sort items by their dependencies using topological sort
        Returns items in the order they should be acquired/used
        """
        if intent not in self.dependencies:
            return []
        
        intent_deps = self.dependencies[intent]
        
        # Create a directed graph
        graph = nx.DiGraph()
        
        # Add all items as nodes
        for item in intent_deps.keys():
            graph.add_node(item)
        
        # Add dependency edges (dependency -> dependent)
        for item, deps in intent_deps.items():
            for dep in deps:
                if dep in intent_deps:  # Only add edge if dependency exists in our item set
                    graph.add_edge(dep, item)
        
        try:
            # Perform topological sort
            sorted_items = list(nx.topological_sort(graph))
            return sorted_items
        except nx.NetworkXError:
            # If there's a cycle, return items in original order
            print(f"Circular dependency detected for intent: {intent}")
            return list(intent_deps.keys())
    
    def get_dependencies_for_item(self, intent: str, item: str) -> List[str]:
        """Get direct dependencies for a specific item"""
        if intent not in self.dependencies:
            return []
        
        intent_deps = self.dependencies[intent]
        return intent_deps.get(item, [])

# Test the dependency engine
if __name__ == "__main__":
    engine = DependencyEngine()
    
    # Test different intents
    test_intents = ["go_hiking", "make_tea", "camping"]
    
    for intent in test_intents:
        print(f"\nIntent: {intent}")
        print("-" * 30)
        
        items = engine.get_items_for_intent(intent)
        print(f"Items needed: {items}")
        
        sorted_items = engine.sort_items_by_dependencies(intent)
        print(f"Dependency order: {sorted_items}")
        
        # Show dependencies for each item
        for item in items:
            deps = engine.get_dependencies_for_item(intent, item)
            if deps:
                print(f"  {item} depends on: {deps}")