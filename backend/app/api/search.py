from fastapi import APIRouter, HTTPException
from ..scrapers.agent import search_with_agent
from ..scrapers.alternative_sources import search_alternative_sources
from ..models import SearchRequest, Listing
from typing import List
import logging

router = APIRouter()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@router.post("/search", response_model=List[Listing])
async def search_listings(query: SearchRequest):
    """Search for housing listings using intelligent agent-based approach"""
    try:
        logger.info("=== INTELLIGENT SEARCH START ===")
        logger.info(f"Search request: {query.dict()}")
        
        # Convert to dict for agent
        params = query.dict()
        
        # Use intelligent agent for search
        try:
            agent_results = await search_with_agent(params)
            logger.info(f"Agent found {len(agent_results)} raw results")
            
        except Exception as e:
            logger.error(f"Agent search failed: {e}")
            agent_results = []
        
        # Apply advanced filtering and scoring
        scored_listings = _score_and_filter_listings(agent_results, params)
        
        logger.info(f"Returning {len(scored_listings)} scored listings")
        logger.info("=== INTELLIGENT SEARCH END ===")
        
        # Return top 30 results
        return scored_listings[:30]
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")

@router.post("/search-alternative", response_model=List[Listing])
async def search_alternative_sources_endpoint(query: SearchRequest):
    """Search for housing listings using alternative sources only"""
    try:
        logger.info("=== ALTERNATIVE SOURCES SEARCH START ===")
        logger.info(f"Search request: {query.dict()}")
        
        # Convert to dict
        params = query.dict()
        
        # Use alternative sources scraper
        try:
            results = await search_alternative_sources(params)
            logger.info(f"Alternative sources found {len(results)} raw results")
            
        except Exception as e:
            logger.error(f"Alternative sources search failed: {e}")
            results = []
        
        # Apply filtering and scoring
        scored_listings = _score_and_filter_listings(results, params)
        
        logger.info(f"Returning {len(scored_listings)} scored listings")
        logger.info("=== ALTERNATIVE SOURCES SEARCH END ===")
        
        # Return top 30 results
        return scored_listings[:30]
        
    except Exception as e:
        logger.error(f"Alternative sources search error: {e}")
        raise HTTPException(status_code=500, detail="Alternative sources search failed")

def _score_and_filter_listings(listings: List[dict], params: dict) -> List[Listing]:
    """Score and filter listings based on user preferences"""
    scored_listings = []
    
    for listing in listings:
        score = 0
        title_lower = listing.get("title", "").lower()
        location_lower = listing.get("location", "").lower()
        
        # Base score
        score += 10
        
        # Price scoring (prefer listings within budget)
        if listing.get("price"):
            if params.get("price_min") and params.get("price_max"):
                target_price = (params["price_min"] + params["price_max"]) / 2
                price_diff = abs(listing["price"] - target_price)
                if price_diff < 100:
                    score += 25
                elif price_diff < 300:
                    score += 15
                elif price_diff < 500:
                    score += 5
            elif params.get("price_max") and listing["price"] <= params["price_max"]:
                score += 20
            elif params.get("price_min") and listing["price"] >= params["price_min"]:
                score += 15
        
        # Location scoring
        if params.get("location"):
            location_keywords = params["location"].lower().split()
            location_matches = sum(1 for keyword in location_keywords if keyword in location_lower)
            if location_matches > 0:
                score += location_matches * 15
        
        # Term scoring
        if params.get("term"):
            term_lower = params["term"].lower()
            if term_lower in title_lower:
                score += 20
            elif any(word in title_lower for word in term_lower.split()):
                score += 10
        
        # Furnished scoring
        if params.get("furnished") is not None:
            furnished_keywords = ["furnished", "furniture", "fully furnished"]
            is_furnished = any(keyword in title_lower for keyword in furnished_keywords)
            if params["furnished"] == is_furnished:
                score += 15
        
        # Lease type scoring
        if params.get("lease_type"):
            lease_type_lower = params["lease_type"].lower()
            if lease_type_lower in title_lower:
                score += 20
            elif "private" in lease_type_lower and "private" in title_lower:
                score += 15
            elif "shared" in lease_type_lower and "shared" in title_lower:
                score += 15
        
        # Source preference (higher preference for UW-specific sources)
        if listing.get("source") == "UW Off-Campus Housing":
            score += 15  # Highest preference for UW-specific source
        elif listing.get("source") == "Kijiji":
            score += 8
        elif listing.get("source") == "Rentals.ca":
            score += 6
        elif listing.get("source") == "Craigslist":
            score += 7  # Good for local listings
        elif listing.get("source") == "Google Search":
            score += 5  # Good for finding diverse sources
        elif listing.get("source") == "Facebook Marketplace":
            score += 4
        elif listing.get("source") == "Reddit r/uwaterloo":
            score += 3
        
        # Penalize listings without price
        if not listing.get("price"):
            score -= 15
        
        # Bonus for listings with detailed information
        if len(title_lower) > 50:
            score += 5
        
        # Create Listing object with score
        listing_obj = Listing(
            title=listing["title"],
            price=listing.get("price"),
            location=listing.get("location"),
            source=listing["source"],
            url=listing["url"]
        )
        
        # Only include listings with positive scores
        if score > 0:
            scored_listings.append((listing_obj, score))
    
    # Sort by score (highest first) and return Listing objects
    scored_listings.sort(key=lambda x: x[1], reverse=True)
    return [listing for listing, score in scored_listings] 