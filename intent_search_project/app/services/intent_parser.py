import re
from typing import Optional, List
import json

class IntentParser:
    """AI-enhanced intent parser using generated dependencies"""
    
    def __init__(self, dependencies_file: str = "data/dependencies.json"):
        self.dependencies_file = dependencies_file
        self.available_intents = self._load_available_intents()
    
    def _load_available_intents(self) -> List[str]:
        """Load available intents from AI-generated dependencies"""
        try:
            with open(self.dependencies_file, 'r') as f:
                dependencies = json.load(f)
            return list(dependencies.keys())
        except:
            return ["general_shopping"]
    
    def extract_intent(self, query: str) -> Optional[str]:
        """Extract intent using AI-generated intents"""
        query_lower = query.lower()
        
        # Score each available intent
        intent_scores = {}
        
        for intent in self.available_intents:
            score = self._calculate_intent_score(query_lower, intent)
            if score > 0:
                intent_scores[intent] = score
        
        # Return highest scoring intent
        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        
        return None
    
    def _calculate_intent_score(self, query: str, intent: str) -> int:
        """Calculate how well query matches intent"""
        
        intent_keywords = {
            'go_hiking': ['hiking', 'hike', 'trek', 'mountain', 'trail', 'outdoor'],
            'prepare_food': ['cook', 'cooking', 'food', 'kitchen', 'recipe', 'meal'],
            'go_camping': ['camp', 'camping', 'tent', 'campfire'],
            'setup_electronics': ['electronics', 'device', 'tech', 'gadget', 'computer'],
            'get_dressed': ['clothing', 'clothes', 'wear', 'dress', 'outfit'],
            'workout': ['fitness', 'exercise', 'gym', 'workout', 'sport'],
            'setup_office': ['office', 'work', 'desk', 'computer', 'business'],
            'automotive_needs': ['car', 'vehicle', 'automotive', 'driving'],
            'sports_activity': ['sport', 'game', 'play', 'activity', 'recreation']
        }
        
        keywords = intent_keywords.get(intent, [intent.replace('_', ' ').split()])
        
        score = 0
        for keyword in keywords:
            if keyword in query:
                score += 1
        
        return score