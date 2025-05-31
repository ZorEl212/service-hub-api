from typing import Dict, List, Optional

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
    def from_lat_lng(lng: float, lat: float) -> "GeoPoint":
        return GeoPoint(coordinates=[lng, lat])  # GeoJSON expects [lng, lat]

class BusinessCategory(str, Enum):
    RESTAURANTS = "restaurant"
    HOME_GARDEN = "home_garden"
    AUTO_SERVICES = "auto_services"
    ELECTRICAL = "electrical"
    HEALTH_BEAUTY = "health_beauty"
    PROFESSIONAL = "professional"
    MORE = "more"

class Subcategory(str, Enum):
    RESTAURANT = "restaurant"
    HOME_GARDEN = "home_garden"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    CAFE = 'cafe'
    TAKEOUT = 'takeout'
    CHINESE = 'chinese'
    RESERVATIONS = 'reservations'
    BURGERS = 'burgers'
    DELIVERY = 'delivery'
    THAI = 'thai'
    LANDSCAPING = 'landscaping'
    CLEANING = 'cleaning'
    PAINTING = 'painting'
    RENOVATION = 'renovation'
    AUTO_REPAIR = 'auto_repair'
    OIL_CHANGE = 'oil_change'
    CAR_WASH = 'car_wash'
    TIRE_SERVICE = 'tire_service'
    DETAILING = 'detailing'
    HAIR_SALON = 'hair_salon'
    SPA = 'spa'
    MASSAGE = 'massage'
    BARRIER = 'barrier'
    NAIL_SALON = 'nail_salon'
    LEGAL = 'legal'
    ACCOUNTING = 'accounting'
    CONSULTING = 'consulting'
    DESIGN = 'design'
    TUTORING = 'tutoring'
    TECH_SUPPORT = 'tech_support'
    MARKETING = 'marketing'
    PET_SERVICES = 'pet_services'
    EVENT_PLANNING = 'event_planning'
    PHOTOGRAPHY = 'photography'
    CATERING = 'catering'
    MOVING = 'moving'

# Category → allowed Subcategories
ALLOWED_SUBCATEGORIES: Dict[BusinessCategory, List[Subcategory]] = {
    BusinessCategory.HOME_GARDEN: [
        Subcategory.PLUMBING,
        Subcategory.LANDSCAPING,
        Subcategory.CLEANING,
        Subcategory.PAINTING,
        Subcategory.RENOVATION,
    ],
    BusinessCategory.RESTAURANTS: [
        Subcategory.RESTAURANT,
        Subcategory.CAFE,
        Subcategory.CHINESE,
        Subcategory.THAI,
        Subcategory.TAKEOUT,
        Subcategory.RESERVATIONS,
        Subcategory.BURGERS,
        Subcategory.DELIVERY,
    ],
    BusinessCategory.AUTO_SERVICES: [
        Subcategory.AUTO_REPAIR,
        Subcategory.OIL_CHANGE,
        Subcategory.CAR_WASH,
        Subcategory.TIRE_SERVICE,
        Subcategory.DETAILING,
    ],
    # Add more mappings as needed
    BusinessCategory.PROFESSIONAL : [
        Subcategory.LEGAL,
        Subcategory.ACCOUNTING,
        Subcategory.CONSULTING,
        Subcategory.DESIGN,
        Subcategory.TUTORING,
        Subcategory.TECH_SUPPORT,
        Subcategory.MARKETING
    ],
    BusinessCategory.HEALTH_BEAUTY: [
        Subcategory.HAIR_SALON,
        Subcategory.SPA,
        Subcategory.MASSAGE,
        Subcategory.BARRIER,
        Subcategory.NAIL_SALON
    ],
    BusinessCategory.MORE: [
        Subcategory.PET_SERVICES,
        Subcategory.EVENT_PLANNING,
        Subcategory.PHOTOGRAPHY,
        Subcategory.CATERING,
        Subcategory.MOVING
    ]
}
