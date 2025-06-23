from fastapi import APIRouter, HTTPException
from typing import List
from ..models.request_models import SparePartRequest
from ..models.response_models import SparePartResponse
from ..services.spare_part_recommender_model import SparePartRecommender

router = APIRouter(prefix="/api/spare-parts", tags=["spare-parts"])
recommender = SparePartRecommender()

@router.post("/recommend", response_model=List[SparePartResponse])
async def recommend_spare_parts(request: SparePartRequest):
    """Get spare part recommendations based on device and issue"""
    try:
        recommendations = recommender.get_recommendations(
            device_model=request.device_model,
            issue_description=request.issue_description,
            brand=request.brand,
            max_results=request.max_results
        )
        return recommendations
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/brands")
async def get_supported_brands():
    """Get list of supported device brands"""
    return recommender.get_supported_brands()

@router.get("/models/{brand}")
async def get_device_models(brand: str):
    """Get device models for a specific brand"""
    return recommender.get_device_models(brand)

@router.get("/health")
async def spare_parts_health():
    """Health check for spare parts service"""
    return {"status": "healthy", "service": "spare_parts_recommender"}