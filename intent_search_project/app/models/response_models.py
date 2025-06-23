from pydantic import BaseModel
from typing import List, Optional

class Item(BaseModel):
    name: str
    category: str
    item_id: Optional[int] = None
    brand: Optional[str] = None
    price: Optional[float] = None
    rating: Optional[float] = None
    image_url: Optional[str] = None  # Add this line

class SearchResponse(BaseModel):
    items: List[Item]
    intent: Optional[str] = None
    total_results: int

# Add this class to your existing response_models.py file
class SparePartResponse(BaseModel):
    part_name: str
    part_number: str
    price: float
    availability: str
    compatibility_score: float
    description: Optional[str] = None
    image_url: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None