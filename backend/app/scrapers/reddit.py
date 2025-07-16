import httpx
import asyncio
from typing import List, Dict, Optional
import re
import logging

logger = logging.getLogger(__name__)

async def search_reddit(params: Dict) -> List[Dict]:
    """
    Search Reddit r/uwaterloo for housing listings
    """
    try:
        logger.info("Searching Reddit...")
        url = "https://www.reddit.com/r/uwaterloo/search.json"
        search_params = {
            "q": "housing OR rent OR apartment OR room",
            "restrict_sr": "on",
            "sort": "new",
            "t": "month"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "application/json",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=search_params, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Reddit returned status {response.status_code}")
                return []
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            listings = []
            for post in posts[:20]:
                post_data = post.get("data", {})
                title = post_data.get("title", "").lower()
                selftext = post_data.get("selftext", "").lower()
                housing_keywords = ["housing", "rent", "apartment", "room", "lease", "sublet"]
                if any(keyword in title or keyword in selftext for keyword in housing_keywords):
                    listing = _extract_reddit_listing(post_data)
                    if listing and _matches_filters(listing, params):
                        listings.append(listing)
            if listings:
                logger.info(f"Reddit: Found {len(listings)} listings")
                return listings
            else:
                logger.warning("Reddit: No listings found.")
                return []
    except Exception as e:
        logger.error(f"Error searching Reddit: {e}")
        return []

def _extract_reddit_listing(post_data: Dict) -> Optional[Dict]:
    try:
        title = post_data.get("title", "").strip()
        if not title or len(title) < 10:
            return None
        text = f"{title} {post_data.get('selftext', '')}"
        price = _extract_price(text)
        location = _extract_location(text) or "Waterloo"
        url = f"https://reddit.com{post_data.get('permalink', '')}"
        return {
            "title": title,
            "price": price,
            "location": location,
            "source": "Reddit",
            "url": url
        }
    except Exception as e:
        logger.debug(f"Error extracting Reddit listing: {e}")
        return None

def _extract_price(text: str) -> Optional[int]:
    price_patterns = [
        r'\$(\d{3,4})',
        r'(\d{3,4})\s*(?:dollars?|cad|per\s*month)',
        r'rent[:\s]*\$?(\d{3,4})',
        r'(\d{3,4})\s*rent'
    ]
    for pattern in price_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                price = int(match.group(1))
                if 400 <= price <= 2000:
                    return price
            except ValueError:
                continue
    return None

def _extract_location(text: str) -> Optional[str]:
    locations = [
        "Columbia", "University Avenue", "Lester", "King Street", 
        "Weber", "Albert", "Erb", "Westmount", "Highland"
    ]
    for location in locations:
        if location.lower() in text.lower():
            return location
    return None

def _matches_filters(listing: Dict, params: Dict) -> bool:
    if listing.get("price"):
        price = listing["price"]
        if params.get("price_min") and price < params["price_min"]:
            return False
        if params.get("price_max") and price > params["price_max"]:
            return False
    if params.get("location"):
        location = params["location"].lower()
        listing_location = listing.get("location", "").lower()
        listing_title = listing.get("title", "").lower()
        if location not in listing_location and location not in listing_title:
            return False
    return True 