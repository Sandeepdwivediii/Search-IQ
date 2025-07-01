from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
from ..services.spare_part_recommender_model import IntelligentSparePartRecommender

router = APIRouter(prefix="/api/spare-parts", tags=["spare-parts"])
recommender = IntelligentSparePartRecommender()

# Define request models directly in this file to avoid import issues
class SparePartRequest(BaseModel):
    device_model: str
    issue_description: str
    brand: str = "samsung"
    max_results: int = 10

class SmartRecommendationRequest(BaseModel):
    problem_description: str
    user_type: Optional[str] = None

class SparePartResponse(BaseModel):
    part_id: str
    part_name: str
    brand: str
    price: float
    availability: str
    compatibility: str
    description: str
    rating: Optional[float] = None
    estimated_delivery: Optional[str] = None
    warranty: Optional[str] = None
    match_reason: Optional[str] = None
    relevance_score: Optional[float] = None

# NEW ENDPOINT - This is what your frontend is calling
@router.post("/intelligent-recommendations")
async def intelligent_recommendations(request: dict):
    """Main endpoint that your frontend calls - Fixed to handle the actual request format"""
    try:
        print(f"📥 Received request: {request}")
        
        # Your frontend sends 'user_problem', let's handle it properly
        user_problem = request.get('user_problem', '')
        user_preferences = request.get('user_preferences', {})
        max_results = request.get('max_results', 10)
        include_analysis = request.get('include_analysis', True)
        
        if not user_problem:
            raise HTTPException(status_code=400, detail="user_problem is required")
        
        print(f"🧠 Processing intelligent recommendation for: {user_problem}")
        
        # Use your intelligent recommender
        result = recommender.get_smart_recommendations(user_problem)
        
        # Format response to match frontend expectations exactly
        formatted_response = {
            "detected_issue": {
                "original_text": result['detected_issue']['original_text'],
                "detected_issues": result['detected_issue']['detected_issues'],
                "device_type": result['detected_issue']['device_type'],
                "urgency": result['detected_issue']['urgency'],
                "keywords_found": result['detected_issue']['keywords_found'],
                "brand_mentioned": result['detected_issue']['brand_mentioned']
            },
            "personalized_message": result['personalized_message'],
            "recommendations": result['recommendations'][:max_results],
            "total_found": result['total_found'],
            "user_profile": result['user_profile'],
            "confidence": "High",
            "confidence_score": 95,
            "response_time": "< 1s",
            "status": "success"
        }
        
        print(f"✅ Sending response with {len(formatted_response['recommendations'])} recommendations")
        return formatted_response
        
    except Exception as e:
        print(f"❌ Error in intelligent recommendations: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/quick-analysis")
async def quick_analysis(request: dict):
    """Quick analysis endpoint for real-time suggestions"""
    try:
        problem_text = request.get('problem_text', '')
        
        if not problem_text:
            return {"analysis": "No text provided"}
        
        # Quick analysis using your existing system
        result = recommender.get_smart_recommendations(problem_text)
        
        return {
            "detected_device": result['detected_issue'].get('device_type', 'Unknown'),
            "detected_issues": result['detected_issue'].get('detected_issues', []),
            "confidence": "High"
        }
        
    except Exception as e:
        print(f"❌ Quick analysis error: {e}")
        return {"analysis": "Analysis failed"}

@router.post("/recommend", response_model=List[SparePartResponse])
async def recommend_spare_parts(request: SparePartRequest):
    """Get spare part recommendations based on device and issue"""
    try:
        # Create problem description from structured request
        problem_description = f"{request.brand} {request.device_model} {request.issue_description}"
        
        # Get recommendations using your intelligent recommender
        result = recommender.get_smart_recommendations(problem_description)
        
        # Convert to response format
        recommendations = []
        for part in result['recommendations']:
            spare_part_response = SparePartResponse(
                part_id=part['part_number'],
                part_name=part['part_name'],
                brand=recommender._extract_brand_from_part(part),
                price=part['price'],
                availability=part['availability'],
                compatibility=part['compatible_models'],
                description=part['description'],
                rating=part.get('rating', 4.0),
                estimated_delivery=part.get('estimated_delivery', '3-5 days'),
                warranty=part.get('warranty', '12 months'),
                match_reason=part.get('match_reason', 'Compatible with your device'),
                relevance_score=part.get('relevance_score', 0.8)
            )
            recommendations.append(spare_part_response)
        
        return recommendations[:request.max_results]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/smart-recommend")
async def smart_recommend(request: SmartRecommendationRequest):
    """Smart recommendation using natural language problem description"""
    try:
        # Use your intelligent recommender directly
        result = recommender.get_smart_recommendations(
            request.problem_description, 
            request.user_type
        )
        
        return {
            "detected_issue": result['detected_issue'],
            "user_profile": result['user_profile'],
            "personalized_message": result['personalized_message'],
            "recommendations": result['recommendations'],
            "total_found": result['total_found'],
            "estimated_delivery": result['estimated_delivery']
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brands")
async def get_supported_brands():
    """Get list of supported device brands"""
    # Extract brands from your parts database
    all_brands = set()
    for device_type, brands_data in recommender.parts_database.items():
        all_brands.update(brands_data.keys())
    
    return {"brands": sorted(list(all_brands))}

@router.get("/models/{brand}")
async def get_device_models(brand: str):
    """Get device models for a specific brand"""
    models = set()
    
    # Search through all device types for the brand
    for device_type, brands_data in recommender.parts_database.items():
        if brand.lower() in brands_data:
            for part in brands_data[brand.lower()]:
                # Extract models from compatible_models field
                compatible_models = part.get('compatible_models', '')
                if compatible_models:
                    # Split by comma and clean up
                    model_list = [model.strip() for model in compatible_models.split(',')]
                    models.update(model_list)
    
    return {"brand": brand, "models": sorted(list(models))}

@router.get("/health")
async def spare_parts_health():
    """Health check for spare parts service"""
    return {
        "status": "healthy", 
        "service": "spare_parts_recommender"
    }