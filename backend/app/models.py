from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SearchRequest(BaseModel):
    gender: Optional[str] = "Any"
    price_min: Optional[int] = None
    price_max: Optional[int] = None
    term: Optional[str] = "Fall"
    location: Optional[str] = None
    furnished: Optional[bool] = False
    lease_type: Optional[str] = "Any"
    stay_length: Optional[str] = "8 months"
    show_browser: Optional[bool] = False

class RelatedLink(BaseModel):
    url: str
    text: str
    reason: str

class Listing(BaseModel):
    title: str
    price: Optional[int]
    location: Optional[str]
    source: str
    url: str
    description: Optional[str] = None
    relevance_score: Optional[float] = None
    related_links: Optional[List[RelatedLink]] = None

class DeepSearchReport(BaseModel):
    total_visited: int
    total_shortlisted: int
    visited_links: List[str]
    shortlisted_links: List[str]
    evaluations: dict
    search_depth: int

class EnhancedSearchResponse(BaseModel):
    success: bool
    listings: List[Listing]
    total_found: int
    deep_search_report: Optional[DeepSearchReport] = None
    search_queries: Optional[List[str]] = None
    llm_queries_used: Optional[bool] = False 