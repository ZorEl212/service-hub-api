from typing import Optional
from pydantic import BaseModel


class SearchFilters(BaseModel):
    q: Optional[str] = None
    category: Optional[str] = None
    location: Optional[str] = None
    rating: Optional[float] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sort: str = "relevance"
    page: int = 1
    limit: int = 10
    user_id: Optional[str] = None
