import httpx
import asyncio
from typing import List, Dict, Optional
from selectolax.parser import HTMLParser
import re
from urllib.parse import urljoin, quote
import logging

logger = logging.getLogger(__name__)

async def search_google(params: Dict) -> List[Dict]:
    """
    Search Google News for housing listings
    """
    try:
        logger.info("Searching Google News...")
        search_terms = []
        if params.get("location"):
            search_terms.append(params["location"])
        if params.get("term"):
            search_terms.append(params["term"])
        search_terms.extend(["student", "housing", "rent", "waterloo"])
        query = " ".join(search_terms)
        url = f"https://www.google.com/search?tbm=nws&q={quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"Google returned status {response.status_code}")
                return []
            parser = HTMLParser(response.text)
            articles = parser.css("div[class*='article']") or parser.css("div[class*='result']") or parser.css("div[class*='item']")
            listings = []
            for article in articles[:15]:
                listing = _extract_google_listing(article)
                if listing and _matches_filters(listing, params):
                    listings.append(listing)
            if listings:
                logger.info(f"Google: Found {len(listings)} listings")
                return listings
            else:
                logger.warning("Google: No listings found.")
                return []
    except Exception as e:
        logger.error(f"Error searching Google: {e}")
        return []

def _extract_google_listing(element) -> Optional[Dict]:
    try:
        title_elem = element.css_first("h3") or element.css_first("h2") or element.css_first("a")
        if not title_elem:
            return None
        title = title_elem.text().strip()
        if not title or len(title) < 10:
            return None
        link_elem = element.css_first("a")
        url = "https://google.com"
        if link_elem:
            href = link_elem.attributes.get("href", "")
            if href and href.startswith("/url?"):
                url_match = re.search(r'url=([^&]+)', href)
                if url_match:
                    url = url_match.group(1)
            elif href.startswith("http"):
                url = href
        snippet_elem = element.css_first("div[class*='snippet']") or element.css_first("span[class*='snippet']") or element.css_first("div")
        snippet = snippet_elem.text().strip() if snippet_elem else ""
        price = _extract_price(f"{title} {snippet}")
        location = _extract_location(f"{title} {snippet}") or "Waterloo"
        return {
            "title": title,
            "price": price,
            "location": location,
            "source": "Google",
            "url": url
        }
    except Exception as e:
        logger.debug(f"Error extracting Google listing: {e}")
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