from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, List

class PropertyDetails(BaseModel):
    city: Optional[str] = Field(None, title="City", description="The city where the person wants to live")
    unit_type: Optional[str] = Field(None, title="Property Type", enum=['house', 'apartment', 'condominium'], description="The type of property that the person wants to live in")
    rooms: Optional[int] = Field(None, title="Number of Rooms", description="The number of rooms that the person wants in the property")
    bathrooms: Optional[int] = Field(None, title="Number of Bathrooms", description="The number of bathrooms that the person wants in the property")
    suites: Optional[int] = Field(None, title="Number of Suites", description="The number of suites that the person wants in the property")
    usable_areas: Optional[List[str]] = Field(None, title="Amenities", description="The amenities that the person wants in the property or condominium if it is one")
    neighborhood: Optional[str] = Field(None, title="Location Neighborhood", description="The neighborhood where the person wants to live")
    parking_spaces: Optional[int] = Field(None, title="Number of Parking Spaces", description="The number of parking spaces that the person wants in the property")
    price_lower: Optional[int] = Field(None, title="Price Range Lower", description="The lower limit of the price range, if just one value is provided, lower is equal to (base_price - 10%)")
    price_upper: Optional[int] = Field(None, title="Price Range Upper", description="The upper limit of the price range, if just one value is provided, upper is equal to (base_price + 10%)")
    user_wants_to_search_for_property: Optional[bool] = Field(None, title="User explicit say that he wants to search for property, must be written", description="If the user wants to search for a property he must explicitly say that he wants to search for a property, must be written. If Search is not explicit the agent should assume that is false.")
