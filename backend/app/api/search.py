from fastapi import APIRouter, HTTPException
from ..scrapers.agent import search_with_agent
from ..scrapers.alternative_sources import search_alternative_sources
from ..scrapers.google_playwright import search_google_playwright
from ..models import SearchRequest, Listing, RelatedLink
from typing import List, Dict, Any
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

@router.post("/search-enhanced")
async def search_enhanced(query: SearchRequest):
    """Enhanced search with LLM queries, deep search, and relevance scoring"""
    try:
        logger.info("=== ENHANCED SEARCH START ===")
        logger.info(f"Search request: {query.dict()}")
        
        # Convert to dict for enhanced search
        params = query.dict()
        
        # Use enhanced search exactly like the working browser test
        try:
            logger.info("Starting real enhanced search (same as browser test)...")
            
            # Run the search in a separate process to avoid Windows subprocess issues
            import subprocess
            import json
            import tempfile
            import os
            
            # Create a temporary file to store the search parameters
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(params, f)
                temp_file = f.name
            
            try:
                # Run the search in a separate process
                logger.info("Running search in separate process to avoid Windows subprocess issues...")
                
                # Use the standalone script
                script_path = os.path.join(os.path.dirname(__file__), '..', '..', 'run_search_standalone.py')
                
                result = subprocess.run([
                    'python', script_path, temp_file
                ], capture_output=True, text=True)  # No timeout - let it run as long as needed
                
                if result.returncode != 0:
                    logger.error(f"Search subprocess failed with return code {result.returncode}")
                    logger.error(f"Error output: {result.stderr}")
                    raise Exception(f"Search subprocess failed: {result.stderr}")
                
                # Parse the result
                search_result = json.loads(result.stdout)
                logger.info(f"Search subprocess completed successfully")
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file):
                    os.unlink(temp_file)
            
            # Extract results and deep search report
            real_listings = search_result.get('listings', [])
            deep_search_report = search_result.get('deep_search_report', {})
            
            # Convert to Listing objects with enhanced fields
            scored_listings = []
            for listing in real_listings:
                # Convert related_links to RelatedLink objects
                related_links = []
                if listing.get("related_links"):
                    for link in listing["related_links"]:
                        if isinstance(link, dict):
                            related_links.append(RelatedLink(
                                url=link.get("url", ""),
                                text=link.get("text", ""),
                                reason=link.get("reason", "")
                            ))
                        elif isinstance(link, str):
                            # Handle case where related_links might be strings
                            related_links.append(RelatedLink(
                                url=link,
                                text="",
                                reason=""
                            ))
                
                listing_obj = Listing(
                    title=listing.get("title", "Housing Listing"),
                    price=listing.get("price"),
                    location=listing.get("location", "Waterloo"),
                    source=listing.get("source", "Google Search"),
                    url=listing.get("url", ""),
                    description=listing.get("description", ""),
                    relevance_score=listing.get("relevance_score", 0.0),
                    related_links=related_links
                )
                scored_listings.append(listing_obj)
            
            # Generate search queries used (for reporting)
            search_queries = [
                f"{params.get('location', 'Waterloo')} student housing rent",
                f"{params.get('location', 'Waterloo')} student housing ${params.get('price_min', 600)}-${params.get('price_max', 1200)}",
                f"{params.get('location', 'Waterloo')} furnished student housing",
                f"{params.get('location', 'Waterloo')} {params.get('lease_type', 'private room')} for rent",
                f"University of Waterloo off campus housing {params.get('term', 'Fall 2024')}"
            ]
            
            # Determine if LLM queries were used
            llm_queries_used = False  # LLM queries are disabled for now
            
            logger.info(f"Enhanced search found {len(scored_listings)} real listings")
            if deep_search_report:
                logger.info(f"Deep search visited {deep_search_report.get('total_visited', 0)} links")
                logger.info(f"Deep search shortlisted {deep_search_report.get('total_shortlisted', 0)} links")
            else:
                logger.info("Deep search was disabled")
            
            return {
                "success": True,
                "listings": scored_listings,
                "total_found": len(scored_listings),
                "deep_search_report": deep_search_report,
                "search_queries": search_queries,
                "llm_queries_used": llm_queries_used
            }
            
        except Exception as e:
            logger.error(f"Enhanced search failed: {e}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
            # Return more detailed error information
            error_detail = f"Enhanced search failed: {str(e)}"
            logger.error(f"Error detail: {error_detail}")
            # Return a proper error response with details
            return {
                "success": False,
                "error": error_detail,
                "listings": [],
                "total_found": 0,
                "deep_search_report": None,
                "search_queries": [],
                "llm_queries_used": False
            }
        
    except Exception as e:
        logger.error(f"Enhanced search error: {e}")
        # Return error response instead of raising HTTPException
        return {
            "success": False,
            "error": f"Enhanced search error: {str(e)}",
            "listings": [],
            "total_found": 0,
            "deep_search_report": None,
            "search_queries": [],
            "llm_queries_used": False
        }

def _score_and_filter_listings_enhanced(listings: List[dict], params: dict) -> List[Listing]:
    """Enhanced scoring and filtering for listings with relevance scores"""
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
                    score += 40  # Perfect price match
                elif price_diff < 300:
                    score += 25
                elif price_diff < 500:
                    score += 15
            elif params.get("price_max") and listing["price"] <= params["price_max"]:
                score += 30
            elif params.get("price_min") and listing["price"] >= params["price_min"]:
                score += 25
        
        # Location scoring
        if params.get("location"):
            location_keywords = params["location"].lower().split()
            location_matches = sum(1 for keyword in location_keywords if keyword in location_lower)
            if location_matches > 0:
                score += location_matches * 20
        
        # Student-specific keywords
        student_keywords = ['student', 'university', 'uw', 'campus', 'academic', 'semester', 'term']
        student_matches = sum(1 for keyword in student_keywords if keyword in title_lower)
        score += student_matches * 10
        
        # Housing keywords
        housing_keywords = ['apartment', 'room', 'rent', 'lease', 'housing', 'accommodation', 'furnished', 'unfurnished']
        housing_matches = sum(1 for keyword in housing_keywords if keyword in title_lower)
        score += housing_matches * 8
        
        # Term scoring
        if params.get("term"):
            term_lower = params["term"].lower()
            if term_lower in title_lower:
                score += 25
            elif any(word in title_lower for word in term_lower.split()):
                score += 15
        
        # Furnished scoring
        if params.get("furnished") is not None:
            furnished_keywords = ["furnished", "furniture", "fully furnished"]
            is_furnished = any(keyword in title_lower for keyword in furnished_keywords)
            if params["furnished"] == is_furnished:
                score += 20
        
        # Lease type scoring
        if params.get("lease_type"):
            lease_type_lower = params["lease_type"].lower()
            if lease_type_lower in title_lower:
                score += 25
            elif "private" in lease_type_lower and "private" in title_lower:
                score += 20
            elif "shared" in lease_type_lower and "shared" in title_lower:
                score += 20
        
        # Source preference
        if listing.get("source") == "UW Off-Campus Housing":
            score += 25
        elif listing.get("source") == "Kijiji":
            score += 15
        elif listing.get("source") == "Rentals.ca":
            score += 12
        elif listing.get("source") == "Google Search":
            score += 10
        
        # Penalize listings without price
        if not listing.get("price"):
            score -= 10
        
        # Create Listing object with enhanced fields
        listing_obj = Listing(
            title=listing["title"],
            price=listing.get("price"),
            location=listing.get("location"),
            source=listing["source"],
            url=listing["url"],
            description=listing.get("description", ""),
            relevance_score=max(0, score),  # Ensure non-negative
            related_links=[]  # Mock for now
        )
        
        # Only include listings with positive scores
        if score > 0:
            scored_listings.append(listing_obj)
    
    # Sort by score (highest first)
    scored_listings.sort(key=lambda x: x.relevance_score, reverse=True)
    return scored_listings 