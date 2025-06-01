from typing import Optional
from pydantic import BaseModel

from models.attributes import BusinessCategory, Subcategory


class SearchFilters(BaseModel):
    q: Optional[str] = None
    category: Optional[BusinessCategory] = None
    subcategory: Optional[Subcategory] = None
    location: Optional[str] = None
    rating: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    distance: Optional[int] = None
    sort: str = "relevance"
    page: int = 1
    limit: int = 10
    user_id: Optional[str] = None
