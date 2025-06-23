from pydantic import BaseModel
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