# es_schemas.py

from pydantic import BaseModel
from typing import List, Optional, Dict
import models

class ServiceProviderSearchDoc(BaseModel):
    id: str
    name: str
    description: str
    phone: str
    category_text: Optional[str]
    service_titles: List[str]
    service_descriptions: List[str]
    category_titles: List[str]
    category_descriptions: List[str]