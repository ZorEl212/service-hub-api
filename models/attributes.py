from typing import Optional

from beanie import Indexed
from pydantic import BaseModel as PydanticModel
from enum import Enum

class GeoPoint(PydanticModel):
    type: str = "Point"
    coordinates: list[float]  # [longitude, latitude]


class Address(PydanticModel):
    street: str
    city: str
    state: str
    zip: str
    location: Optional[Indexed(GeoPoint, index_type="2dsphere")]  # this sets up index!

    @staticmethod
    def from_lat_lng(lat: float, lng: float) -> "GeoPoint":
        return GeoPoint(coordinates=[lng, lat])  # GeoJSON expects [lng, lat]

class BusinessCategory(str, Enum):
    RESTAURANT = "restaurant"
    HOME_GARDEN = "home_garden"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"

class Subcategory(str, Enum):
    RESTAURANT = "restaurant"
    HOME_GARDEN = "home_garden"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"

