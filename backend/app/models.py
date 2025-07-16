from pydantic import BaseModel
from typing import Optional

class SearchRequest(BaseModel):
    gender: Optional[str] = "Any"
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    term: Optional[str] = "Fall"
    location: Optional[str] = None
    furnished: Optional[bool] = False
    lease_type: Optional[str] = "Any"
    stay_length: Optional[str] = "8 months"

class Listing(BaseModel):
    title: str
    price: Optional[int]
    location: Optional[str]
    source: str
    url: str 