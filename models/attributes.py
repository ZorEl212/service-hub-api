from pydantic import BaseModel as PydanticModel


class Location(PydanticModel):
    lat: float
    lng: float

class Address(PydanticModel):
    street: str
    city: str
    state: str
    zip: str
    location: Location