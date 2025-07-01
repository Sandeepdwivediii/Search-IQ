import re
import json
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import random

class IntelligentSparePartRecommender:
    def __init__(self):
        self.user_profiles = self._create_user_profiles()
        self.keyword_mappings = self._setup_comprehensive_keyword_mappings()
        self.parts_database = self._create_comprehensive_parts_database()
        self.purchase_patterns = self._create_purchase_patterns()
        # NEW: Hardcoded user purchase history for demo
        self.user_purchase_history = self._create_realistic_purchase_history()
        
    def _create_realistic_purchase_history(self):
        """Create realistic user purchase history for intelligent recommendations"""
        return {
            "user_123": {  # Demo user
                "purchases": [
                    {
                        "product": "Samsung Galaxy S24 Ultra",
                        "purchase_date": "2024-03-15",
                        "price": 89999,
                        "warranty_until": "2026-03-15"
                    },
                    {
                        "product": "Dell XPS 15 Laptop",
                        "model": "9520",
                        "purchase_date": "2022-11-05",
                        "price": 125000,
                        "warranty_until": "2024-11-05"
                    },
                    {
                        "product": "Sony WH-1000XM5 Headphones",
                        "purchase_date": "2024-01-10",
                        "price": 25000,
                        "warranty_until": "2025-01-10"
                    }
                ],
                "preferred_brands": ["samsung", "dell", "sony"],
                "spending_profile": "premium",
                "total_spent": 239999
            },
            "user_456": {  # Another demo user
                "purchases": [
                    {
                        "product": "iPhone 15 Pro Max",
                        "purchase_date": "2024-01-20",
                        "price": 134900,
                        "warranty_until": "2025-01-20"
                    },
                    {
                        "product": "MacBook Pro M3",
                        "purchase_date": "2023-12-15",
                        "price": 199900,
                        "warranty_until": "2024-12-15"
                    }
                ],
                "preferred_brands": ["apple"],
                "spending_profile": "premium",
                "total_spent": 334800
            },
            "user_789": {  # Budget user
                "purchases": [
                    {
                        "product": "Xiaomi Redmi Note 13 Pro",
                        "purchase_date": "2024-02-10",
                        "price": 18999,
                        "warranty_until": "2025-02-10"
                    },
                    {
                        "product": "OnePlus Nord CE 3",
                        "purchase_date": "2023-08-15",
                        "price": 24999,
                        "warranty_until": "2024-08-15"
                    }
                ],
                "preferred_brands": ["xiaomi", "oneplus"],
                "spending_profile": "budget",
                "total_spent": 43998
            }
        }
    
    def _create_user_profiles(self):
        """Create diverse user profiles with purchase history"""
        return {
            "tech_enthusiast": {
                "recent_purchases": [
                    "Samsung Galaxy S24 Ultra", "iPhone 15 Pro", "OnePlus 12",
                    "Xiaomi 14 Ultra", "Google Pixel 8 Pro"
                ],
                "brand_preferences": ["samsung", "apple", "oneplus", "xiaomi"],
                "device_types": ["phone"],
                "spending_range": "premium"
            },
            "budget_conscious": {
                "recent_purchases": [
                    "Xiaomi Redmi Note 13", "Realme 12 Pro", "Samsung Galaxy A54",
                    "OnePlus Nord CE 3", "Motorola Edge 40"
                ],
                "brand_preferences": ["xiaomi", "realme", "oneplus", "motorola"],
                "device_types": ["phone"],
                "spending_range": "budget"
            },
            "professional": {
                "recent_purchases": [
                    "iPhone 15 Pro Max", "Samsung Galaxy S24 Ultra", "Google Pixel 8 Pro",
                    "OnePlus 12", "Sony Xperia 1 V"
                ],
                "brand_preferences": ["apple", "samsung", "google", "sony"],
                "device_types": ["phone"],
                "spending_range": "premium"
            },
            "apple_fan": {
                "recent_purchases": [
                    "iPhone 15 Pro Max", "iPhone 14 Pro", "iPhone 13 Pro"
                ],
                "brand_preferences": ["apple"],
                "device_types": ["phone"],
                "spending_range": "premium"
            }
        }
    
    def _setup_comprehensive_keyword_mappings(self):
        """Comprehensive keyword mappings for phone issues"""
        return {
            # Phone Issues
            "battery": {
                "keywords": ["battery", "charging", "power", "drain", "dead", "backup", "life", "charge"],
                "devices": ["phone"],
                "severity": ["critical", "high"]
            },
            "screen": {
                "keywords": ["screen", "display", "touch", "cracked", "broken", "black", "flickering"],
                "devices": ["phone"],
                "severity": ["critical", "high"]
            },
            "camera": {
                "keywords": ["camera", "lens", "photo", "video", "blurry", "focus", "flash"],
                "devices": ["phone"],
                "severity": ["medium", "low"]
            },
            "audio": {
                "keywords": ["sound", "audio", "speaker", "volume", "headphone", "mic", "noise"],
                "devices": ["phone"],
                "severity": ["medium", "high"]
            },
            "performance": {
                "keywords": ["slow", "lag", "performance", "speed", "hang", "freeze", "crash"],
                "devices": ["phone"],
                "severity": ["medium", "high"]
            },
            "connectivity": {
                "keywords": ["wifi", "bluetooth", "network", "connection", "internet", "signal"],
                "devices": ["phone"],
                "severity": ["medium", "high"]
            },
            "storage": {
                "keywords": ["storage", "memory", "space", "full"],
                "devices": ["phone"],
                "severity": ["medium", "low"]
            }
        }
    
    def _create_comprehensive_parts_database(self):
        """Create a comprehensive phone parts database with real product images"""
        return {
            # Phone Parts Only
            "phone": {
                "samsung": [
                    {
            "part_name": "Samsung Galaxy S24 Ultra Battery Pack (5000mAh)",
            "part_number": "SG-BAT-5000-S24U",
            "price": 2999,
            "category": "battery",
            "compatible_models": "Galaxy S24 Ultra, S23 Ultra",
            "availability": "In Stock",
            "description": "Original Samsung battery for Galaxy S24 Ultra with 2-year warranty",
            "rating": 4.8,
            "warranty": "24 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71vK8sTkBcL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "Samsung Galaxy S24 AMOLED Display Assembly",
            "part_number": "SG-DISP-AMOLED-S24",
            "price": 15999,
            "category": "screen",
            "compatible_models": "Galaxy S24, S24+, S24 Ultra",
            "availability": "In Stock",
            "description": "Premium AMOLED display with touch digitizer for Galaxy S24",
            "rating": 4.9,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61JCWEhYOoL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "Samsung Galaxy S24 Camera Module (200MP)",
            "part_number": "SG-CAM-200MP-S24U",
            "price": 8999,
            "category": "camera",
            "compatible_models": "Galaxy S24 Ultra",
            "availability": "Limited Stock",
            "description": "High-resolution 200MP main camera sensor for S24 Ultra",
            "rating": 4.7,
            "warranty": "6 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/KHSnZFDmdEQN2VbV.medium"
        },
        {
            "part_name": "Samsung Galaxy Speaker Assembly",
            "part_number": "SG-SPKR-STEREO-S24",
            "price": 1999,
            "category": "audio",
            "compatible_models": "Galaxy S24, S23, A54, A34",
            "availability": "In Stock",
            "description": "Stereo speaker set with enhanced bass for Galaxy S24",
            "rating": 4.6,
            "warranty": "6 months",
            "image_url": "https://phoneparts.co.uk/wp-content/uploads/2024/03/GH96-15540A-600x600.jpg"
        },
        {
            "part_name": "Samsung Galaxy Charging Port Assembly",
            "part_number": "SG-PORT-USBC-S24",
            "price": 1499,
            "category": "battery",
            "compatible_models": "All Galaxy S24 series, S23 series",
            "availability": "In Stock",
            "description": "USB-C charging port with 45W fast charging support",
            "rating": 4.5,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61rKk0YBOuL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "Samsung Galaxy A54 Battery (5000mAh)",
            "part_number": "SG-BAT-5000-A54",
            "price": 1899,
            "category": "battery",
            "compatible_models": "Galaxy A54, A34, A53",
            "availability": "In Stock",
            "description": "Long-lasting battery for Samsung Galaxy A54 with fast charging",
            "rating": 4.4,
            "warranty": "18 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71vK8sTkBcL._AC_UL600_SR600,600_.jpg"
        }
    ],
    "apple": [
        {
            "part_name": "iPhone 15 Pro Max Battery (4441mAh)",
            "part_number": "IP-BAT-4441-15PM",
            "price": 6999,
            "category": "battery",
            "compatible_models": "iPhone 15 Pro Max",
            "availability": "In Stock",
            "description": "Genuine Apple battery replacement for iPhone 15 Pro Max",
            "rating": 4.9,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61QcC2QrpCL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "iPhone 15 Pro OLED Screen (6.7 inch)",
            "part_number": "IP-OLED-6.7-15P",
            "price": 24999,
            "category": "screen",
            "compatible_models": "iPhone 15 Pro Max",
            "availability": "In Stock",
            "description": "Super Retina XDR OLED display assembly with ProMotion",
            "rating": 4.8,
            "warranty": "12 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/mMCJuD1MdPCqPm6u.medium"
        },
        {
            "part_name": "iPhone 15 Pro Camera System (48MP)",
            "part_number": "IP-CAM-48MP-15P",
            "price": 12999,
            "category": "camera",
            "compatible_models": "iPhone 15 Pro, 15 Pro Max",
            "availability": "In Stock",
            "description": "Pro camera system with LiDAR scanner and 5x telephoto",
            "rating": 4.9,
            "warranty": "6 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/oJrA2SjsQ4fDEOKV.medium"
        },
        {
            "part_name": "iPhone 15 Lightning to USB-C Port",
            "part_number": "IP-PORT-USBC-15",
            "price": 2999,
            "category": "battery",
            "compatible_models": "iPhone 15, 15 Plus, 15 Pro, 15 Pro Max",
            "availability": "In Stock",
            "description": "USB-C charging port assembly for iPhone 15 series",
            "rating": 4.6,
            "warranty": "12 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/ZJjZaZwDdDAJyNfG.medium"
        },
        {
            "part_name": "iPhone 14 Pro Battery (3200mAh)",
            "part_number": "IP-BAT-3200-14P",
            "price": 5999,
            "category": "battery",
            "compatible_models": "iPhone 14 Pro",
            "availability": "In Stock",
            "description": "High-quality replacement battery for iPhone 14 Pro",
            "rating": 4.7,
            "warranty": "12 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/kp6q5OVf3nJYP3LR.medium"
        }
    ],
    "xiaomi": [
        {
            "part_name": "Xiaomi Redmi Note 13 Pro Battery (5000mAh)",
            "part_number": "XI-BAT-5000-RN13P",
            "price": 1599,
            "category": "battery",
            "compatible_models": "Redmi Note 13 Pro, Note 13 Pro+",
            "availability": "In Stock",
            "description": "Long-lasting battery with 67W fast charging support",
            "rating": 4.4,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61aLt5h7hzL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "Xiaomi 14 Ultra Camera Module (50MP)",
            "part_number": "XI-CAM-50MP-14U",
            "price": 4999,
            "category": "camera",
            "compatible_models": "Xiaomi 14 Ultra",
            "availability": "In Stock",
            "description": "Leica-tuned camera system with 50MP main sensor",
            "rating": 4.6,
            "warranty": "6 months",
            "image_url": "https://www.techinn.com/f/13840/138402647/xiaomi-redmi-note-13-pro-plus-camera-lens.jpg"
        },
        {
            "part_name": "Xiaomi Redmi AMOLED Display (6.67 inch)",
            "part_number": "XI-DISP-AMOLED-6.67",
            "price": 3999,
            "category": "screen",
            "compatible_models": "Redmi Note 13 Pro, 12 Pro",
            "availability": "In Stock",
            "description": "120Hz AMOLED display with Gorilla Glass protection",
            "rating": 4.3,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61qX8Y4u0xL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "Xiaomi USB-C Charging Port",
            "part_number": "XI-PORT-USBC-2024",
            "price": 899,
            "category": "battery",
            "compatible_models": "All Xiaomi phones with USB-C",
            "availability": "In Stock",
            "description": "Universal USB-C charging port for Xiaomi devices",
            "rating": 4.2,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61rKk0YBOuL._AC_UL600_SR600,600_.jpg"
        }
    ],
    "oneplus": [
        {
            "part_name": "OnePlus 12 Battery (5400mAh)",
            "part_number": "OP-BAT-5400-12",
            "price": 2299,
            "category": "battery",
            "compatible_models": "OnePlus 12",
            "availability": "In Stock",
            "description": "High-capacity battery with 100W SuperVOOC charging",
            "rating": 4.7,
            "warranty": "18 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71vK8sTkBcL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "OnePlus Nord CE 3 Display (6.7 inch)",
            "part_number": "OP-DISP-6.7-NCE3",
            "price": 2999,
            "category": "screen",
            "compatible_models": "OnePlus Nord CE 3",
            "availability": "In Stock",
            "description": "120Hz AMOLED display for OnePlus Nord CE 3",
            "rating": 4.4,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61JCWEhYOoL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "OnePlus Camera Module (50MP Hasselblad)",
            "part_number": "OP-CAM-50MP-H12",
            "price": 5999,
            "category": "camera",
            "compatible_models": "OnePlus 12, 11",
            "availability": "Limited Stock",
            "description": "Hasselblad-tuned camera system with 50MP main sensor",
            "rating": 4.8,
            "warranty": "6 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/KHSnZFDmdEQN2VbV.medium"
        }
    ],
    "realme": [
        {
            "part_name": "Realme 12 Pro+ Battery (5000mAh)",
            "part_number": "RM-BAT-5000-12PP",
            "price": 1799,
            "category": "battery",
            "compatible_models": "Realme 12 Pro+, 12 Pro",
            "availability": "In Stock",
            "description": "Fast-charging battery with 67W SuperDart charging",
            "rating": 4.3,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61aLt5h7hzL._AC_UL600_SR600,600_.jpg"
        },
        {
            "part_name": "Realme AMOLED Display (6.7 inch)",
            "part_number": "RM-DISP-AMOLED-6.7",
            "price": 3299,
            "category": "screen",
            "compatible_models": "Realme 12 Pro+, 11 Pro+",
            "availability": "In Stock",
            "description": "Curved AMOLED display with 120Hz refresh rate",
            "rating": 4.2,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/61qX8Y4u0xL._AC_UL600_SR600,600_.jpg"
        }
    ],
    "google": [
        {
            "part_name": "Google Pixel 8 Pro Battery (5050mAh)",
            "part_number": "GP-BAT-5050-8P",
            "price": 4999,
            "category": "battery",
            "compatible_models": "Google Pixel 8 Pro",
            "availability": "In Stock",
            "description": "Original Google battery with adaptive charging technology",
            "rating": 4.6,
            "warranty": "12 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/XkGHaOF6lE2cChyy.medium"
        },
        {
            "part_name": "Google Pixel Camera Bar (50MP)",
            "part_number": "GP-CAM-50MP-8P",
            "price": 7999,
            "category": "camera",
            "compatible_models": "Google Pixel 8 Pro, 8",
            "availability": "Limited Stock",
            "description": "AI-enhanced camera system with computational photography",
            "rating": 4.9,
            "warranty": "6 months",
            "image_url": "https://guide-images.cdn.ifixit.com/igi/oJrA2SjsQ4fDEOKV.medium"
        }
    ],
    "motorola": [
        {
            "part_name": "Motorola Edge 40 Battery (4400mAh)",
            "part_number": "MT-BAT-4400-E40",
            "price": 1999,
            "category": "battery",
            "compatible_models": "Motorola Edge 40, Edge 30",
            "availability": "In Stock",
            "description": "TurboPower fast charging battery for Motorola Edge",
            "rating": 4.1,
            "warranty": "12 months",
            "image_url": "https://images-na.ssl-images-amazon.com/images/I/71vK8sTkBcL._AC_UL600_SR600,600_.jpg"
                }
            ]
        }
    }
    def _create_purchase_patterns(self):
        """Create realistic purchase patterns for personalization"""
        patterns = {
            "recent_buyer": "Based on your recent purchase",
            "loyal_customer": "As a valued customer who has bought",
            "brand_loyal": "Since you prefer",
            "first_time": "Welcome! For your",
            "frequent": "Your purchase history shows you often buy"
        }
        return patterns
    
    def get_smart_recommendations(self, user_problem: str, user_type: str = None, user_id: str = "user_123"):
        """
        ENHANCED: Main recommendation function with purchase history analysis
        """
        print(f"🔍 Analyzing problem: '{user_problem}' for user: {user_id}")
        
        # Get user's actual purchase history
        user_purchases = self.user_purchase_history.get(user_id, {})
        
        # Auto-detect user type if not provided
        if not user_type:
            user_type = self._detect_user_type(user_problem)
        
        # Extract issue details
        issue_analysis = self._analyze_problem(user_problem)
        
        # ENHANCED: Find user's specific device from purchase history
        specific_device = self._find_users_device(issue_analysis, user_purchases)
        
        # Get user profile
        user_profile = self.user_profiles.get(user_type, self.user_profiles["tech_enthusiast"])
        
        # ENHANCED: Update user profile with actual purchase data
        if user_purchases:
            user_profile["recent_purchases"] = [p["product"] for p in user_purchases.get("purchases", [])]
            user_profile["brand_preferences"] = user_purchases.get("preferred_brands", user_profile["brand_preferences"])
            user_profile["spending_range"] = user_purchases.get("spending_profile", user_profile["spending_range"])
        
        # Find matching parts with specific device context
        recommendations = self._find_intelligent_matches(issue_analysis, user_profile, specific_device)
        
        # Generate personalized message with specific device
        personalized_message = self._generate_personalized_message(user_profile, issue_analysis, specific_device)
        
        result = {
            "detected_issue": issue_analysis,
            "user_profile": user_type,
            "personalized_message": personalized_message,
            "recommendations": recommendations,
            "total_found": len(recommendations),
            "estimated_delivery": self._get_delivery_estimate(),
            "specific_device": specific_device,
            "user_purchase_history": user_purchases.get("purchases", [])[:3]  # Show last 3 purchases
        }
        
        print(f"✅ Found {len(recommendations)} recommendations for {specific_device or 'detected device'}")
        return result
    
    def _find_users_device(self, issue_analysis: Dict, user_purchases: Dict) -> str:
        """NEW: Find user's specific device from purchase history"""
        device_type = issue_analysis.get("device_type")
        brand_mentioned = issue_analysis.get("brand_mentioned")
        
        if not device_type or not user_purchases.get("purchases"):
            return None
        
        # Look for matching devices in purchase history
        for purchase in user_purchases["purchases"]:
            product = purchase["product"].lower()
            
            # Match phone devices
            if device_type == "phone" and any(keyword in product for keyword in ["phone", "galaxy", "iphone", "redmi", "oneplus", "pixel", "edge"]):
                if not brand_mentioned or brand_mentioned in product:
                    print(f"🎯 Found user's device: {purchase['product']}")
                    return purchase["product"]
        
        return None
    
    def _detect_user_type(self, problem_text: str) -> str:
        """Intelligently detect user type from problem description"""
        problem_lower = problem_text.lower()
        
        # Check for premium device mentions
        premium_keywords = ["pro", "ultra", "max", "premium", "expensive", "flagship"]
        budget_keywords = ["cheap", "budget", "affordable", "basic", "old", "redmi", "realme"]
        professional_keywords = ["work", "office", "business", "professional", "meeting"]
        apple_keywords = ["iphone", "apple"]
        
        if any(keyword in problem_lower for keyword in apple_keywords):
            return "apple_fan"
        elif any(keyword in problem_lower for keyword in premium_keywords):
            return "professional"
        elif any(keyword in problem_lower for keyword in budget_keywords):
            return "budget_conscious"
        elif any(keyword in problem_lower for keyword in professional_keywords):
            return "professional"
        else:
            return "tech_enthusiast"
    
    def _analyze_problem(self, problem_text: str) -> Dict:
        """Advanced problem analysis with NLP-like processing"""
        analysis = {
            "original_text": problem_text,
            "detected_issues": [],
            "device_type": "phone",  # Only phone for this version
            "urgency": "medium",
            "keywords_found": [],
            "brand_mentioned": None
        }
        
        problem_lower = problem_text.lower()
        
        # Detect brand
        brands = ["samsung", "apple", "xiaomi", "oneplus", "realme", "google", "motorola"]
        for brand in brands:
            if brand in problem_lower:
                analysis["brand_mentioned"] = brand
                break
        
        # Detect issues
        for issue_type, issue_data in self.keyword_mappings.items():
            for keyword in issue_data["keywords"]:
                if keyword in problem_lower:
                    analysis["detected_issues"].append(issue_type)
                    analysis["keywords_found"].append(keyword)
                    
                    # Set urgency based on issue severity
                    if "critical" in issue_data["severity"]:
                        analysis["urgency"] = "high"
                    elif "high" in issue_data["severity"] and analysis["urgency"] != "high":
                        analysis["urgency"] = "medium"
        
        # Remove duplicates
        analysis["detected_issues"] = list(set(analysis["detected_issues"]))
        analysis["keywords_found"] = list(set(analysis["keywords_found"]))
        
        return analysis
    
    def _find_intelligent_matches(self, issue_analysis: Dict, user_profile: Dict, specific_device: str = None) -> List[Dict]:
        """ENHANCED: Find matching parts using user's specific device"""
        recommendations = []
        
        device_type = "phone"  # Only phone parts
        detected_issues = issue_analysis["detected_issues"]
        brand_preference = issue_analysis["brand_mentioned"]
        
        # Get parts for phones
        device_parts = self.parts_database.get(device_type, {})
        
        # Prioritize brands
        brands_to_check = []
        if brand_preference:
            brands_to_check.append(brand_preference)
        brands_to_check.extend(user_profile.get("brand_preferences", []))
        brands_to_check.extend(device_parts.keys())
        
        # Remove duplicates while preserving order
        brands_to_check = list(dict.fromkeys(brands_to_check))
        
        for brand in brands_to_check:
            if brand in device_parts:
                for part in device_parts[brand]:
                    score = self._calculate_intelligent_score(part, issue_analysis, user_profile, specific_device)
                    if score > 0.2:  # Lower threshold for better results
                        enhanced_part = part.copy()
                        enhanced_part["relevance_score"] = score
                        enhanced_part["match_reason"] = self._get_match_reason(part, issue_analysis, specific_device)
                        enhanced_part["estimated_delivery"] = self._get_delivery_estimate()
                        recommendations.append(enhanced_part)
        
        # Sort by relevance score
        recommendations.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return recommendations[:8]  # Return top 8 recommendations

    def _calculate_intelligent_score(self, part: Dict, issue_analysis: Dict, user_profile: Dict, specific_device: str = None) -> float:
        """ENHANCED: Advanced scoring with specific device matching"""
        score = 0.0
        
        # Issue category match (highest priority)
        if part["category"] in issue_analysis["detected_issues"]:
            score += 0.6
        
        # ENHANCED: Specific device compatibility
        if specific_device and specific_device.lower() in part["compatible_models"].lower():
            score += 0.3  # Big bonus for exact device match
            print(f"🎯 Exact device match: {part['part_name']} for {specific_device}")
        
        # Brand preference
        part_brand = self._extract_brand_from_part(part)
        if part_brand in user_profile.get("brand_preferences", []):
            score += 0.2
        
        # Price range compatibility
        spending_range = user_profile.get("spending_range", "mid_range")
        price_score = self._calculate_price_compatibility(part["price"], spending_range)
        score += price_score * 0.15
        
        # Availability bonus
        if part["availability"] == "In Stock":
            score += 0.1
        elif part["availability"] == "Limited Stock":
            score += 0.05
        
        # Rating bonus
        rating = part.get("rating", 4.0)
        score += (rating - 3.0) * 0.05
        
        # Urgency matching
        if issue_analysis["urgency"] == "high" and part["availability"] == "In Stock":
            score += 0.1
        
        return min(score, 1.0)

    def _calculate_price_compatibility(self, price: float, spending_range: str) -> float:
        """Calculate how well the price matches user's spending pattern"""
        if spending_range == "budget":
            if price <= 2000:
                return 1.0
            elif price <= 5000:
                return 0.7
            else:
                return 0.3
        elif spending_range == "mid_range":
            if 1000 <= price <= 10000:
                return 1.0
            elif price <= 15000:
                return 0.8
            else:
                return 0.5
        elif spending_range == "premium":
            if price >= 5000:
                return 1.0
            elif price >= 2000:
                return 0.8
            else:
                return 0.6
        return 0.5

    def _extract_brand_from_part(self, part: Dict) -> str:
        """Extract brand from part name"""
        part_name = part["part_name"].lower()
        brands = ["samsung", "apple", "xiaomi", "oneplus", "realme", "google", "motorola"]
        for brand in brands:
            if brand in part_name:
                return brand
        return "unknown"

    def _get_match_reason(self, part: Dict, issue_analysis: Dict, specific_device: str = None) -> str:
        """ENHANCED: Generate explanation with specific device context"""
        reasons = []
        
        if specific_device and specific_device.lower() in part["compatible_models"].lower():
            reasons.append(f"Perfect match for your {specific_device}")
        
        if part["category"] in issue_analysis["detected_issues"]:
            reasons.append(f"Directly addresses {part['category']} issues")
        
        if part["availability"] == "In Stock":
            reasons.append("Available for immediate shipping")
        
        if part.get("rating", 0) >= 4.5:
            reasons.append("Highly rated by customers")
        
        return " • ".join(reasons) if reasons else "Compatible with your device"

    def _generate_personalized_message(self, user_profile: Dict, issue_analysis: Dict, specific_device: str = None) -> str:
        """ENHANCED: Generate message with specific device context"""
        if specific_device:
            device_context = f"your {specific_device}"
        else:
            recent_purchase = user_profile["recent_purchases"][0] if user_profile["recent_purchases"] else "your phone"
            device_context = recent_purchase
        
        urgency = issue_analysis["urgency"]
        
        urgency_messages = {
            "high": f"We understand this is urgent! Here are immediate solutions for {device_context}:",
            "medium": f"Based on our analysis of {device_context}, we've found these compatible parts:",
            "low": f"Here are some recommended parts for {device_context}:"
        }
        
        return urgency_messages.get(urgency, f"Based on your {device_context}, we've found these compatible parts:")

    def _get_delivery_estimate(self) -> str:
        """Generate realistic delivery estimates"""
        estimates = ["1-2 days", "2-3 days", "3-5 days", "5-7 days"]
        return random.choice(estimates)

    def display_recommendations(self, result: Dict):
        """Display recommendations in a nice format"""
        print("=" * 80)
        print("🔧 INTELLIGENT PHONE PARTS RECOMMENDATION SYSTEM")
        print("=" * 80)
        
        if result.get("specific_device"):
            print(f"\n🎯 YOUR DEVICE: {result['specific_device']}")
        
        print(f"\n📱 DETECTED ISSUE: {', '.join(result['detected_issue']['detected_issues'])}")
        print(f"🎯 DEVICE TYPE: {result['detected_issue']['device_type']}")
        print(f"⚡ URGENCY: {result['detected_issue']['urgency'].upper()}")
        print(f"👤 USER PROFILE: {result['user_profile'].replace('_', ' ').title()}")
        print(f"\n💬 {result['personalized_message']}")
        print(f"\n🔍 FOUND {result['total_found']} COMPATIBLE PARTS:")
        print("-" * 80)
        
        for i, part in enumerate(result['recommendations'], 1):
            print(f"\n{i}. {part['part_name']}")
            print(f"   💰 Price: ₹{part['price']}")
            print(f"   📦 Stock: {part['availability']}")
            print(f"   ⭐ Rating: {part.get('rating', 'N/A')}/5.0")
            print(f"   🚚 Delivery: {part['estimated_delivery']}")
            print(f"   ✅ Why recommended: {part['match_reason']}")
            print(f"   🔧 Part #: {part['part_number']}")
            if part.get('warranty'):
                print(f"   🛡️ Warranty: {part['warranty']}")
            print(f"   📝 {part['description']}")
            print(f"   🎯 Relevance Score: {part['relevance_score']:.2f}")
            
        if result.get("user_purchase_history"):
            print(f"\n📋 YOUR RECENT PURCHASES:")
            for purchase in result["user_purchase_history"]:
                print(f"   • {purchase['product']} (₹{purchase['price']:,}) - {purchase['purchase_date']}")
            
        print("\n" + "=" * 80)
        print("✨ Recommendations powered by AI-driven compatibility analysis")
        print("=" * 80)

# For backward compatibility - create an alias
SparePartRecommender = IntelligentSparePartRecommender

# Usage Examples
if __name__ == "__main__":
  recommender = IntelligentSparePartRecommender()
  
  # Test cases with different user scenarios
  test_cases = [
      {
          "problem": "my phone battery is not working",
          "user_id": "user_123",
          "description": "User with Samsung Galaxy S24 Ultra"
      },
      {
          "problem": "my iPhone screen is cracked",
          "user_id": "user_456",
          "description": "User with iPhone 15 Pro Max"
      },
      {
          "problem": "my redmi phone camera is blurry",
          "user_id": "user_789",
          "description": "User with Xiaomi Redmi Note 13 Pro"
      },
      {
          "problem": "my phone speaker is not working",
          "user_id": "user_123",
          "description": "User with Samsung Galaxy S24 Ultra"
      },
      {
          "problem": "my oneplus charging port is loose",
          "user_id": "user_789",
          "description": "User with OnePlus Nord CE 3"
      }
  ]
  
  print("🚀 TESTING ENHANCED PHONE PARTS RECOMMENDER\n")
  
  for i, test_case in enumerate(test_cases, 1):
      print(f"\n{'='*20} TEST CASE {i} {'='*20}")
      print(f"Scenario: {test_case['description']}")
      print(f"Problem: {test_case['problem']}")
      
      result = recommender.get_smart_recommendations(
          test_case["problem"], 
          user_id=test_case["user_id"]
      )
      recommender.display_recommendations(result)
      
      if i < len(test_cases):
          input("\nPress Enter to continue to next test case...")