from pydantic import BaseModel, Field
from typing import Optional

class SearchRequest(BaseModel):
    query: str

class SearchConfig(BaseModel):
    max_results: int = 10
    include_dependencies: bool = True

class SparePartRequest(BaseModel):
    device_model: str
    issue_description: str
    brand: str = "samsung"
    max_results: int = 10

class SmartRecommendationRequest(BaseModel):
    problem_description: str = Field(..., description="Natural language description of the problem")
    user_type: Optional[str] = Field(None, description="User type (tech_enthusiast, home_owner, budget_conscious, professional)")