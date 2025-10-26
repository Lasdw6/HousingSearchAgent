import httpx
import asyncio
from typing import List, Dict, Optional
from selectolax.parser import HTMLParser
import re
from urllib.parse import urljoin
import logging

logger = logging.getLogger(__name__)

async def search_uw_offcampus(params: Dict) -> List[Dict]:
    """
    Search UW Off-Campus Housing for listings
    """
    try:
        logger.info("Searching UW Off-Campus Housing...")
        url = "https://offcampushousing.uwaterloo.ca/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            if response.status_code != 200:
                logger.warning(f"UW Off-Campus returned status {response.status_code}")
                return []
            parser = HTMLParser(response.text)
            selectors = [
                "div[class*='listing']",
                "div[class*='property']",
                "div[class*='rental']",
                "article[class*='listing']",
                "div[class*='item']"
            ]
            listings = []
            for selector in selectors:
                elements = parser.css(selector)
                if elements:
                    for element in elements[:20]:
                        listing = _extract_uw_listing(element)
                        if listing and _matches_filters(listing, params):
                            listing["priority"] = 10
                            listings.append(listing)
                    break
            if listings:
                logger.info(f"UW Off-Campus: Found {len(listings)} listings")
                return listings
            else:
                logger.warning("UW Off-Campus: No listings found.")
                return []
    except Exception as e:
        logger.error(f"Error searching UW Off-Campus: {e}")
        return []

def _extract_uw_listing(element) -> Optional[Dict]:
    try:
        title_elem = element.css_first("h3") or element.css_first("h2") or element.css_first("h4") or element.css_first("a")
        if not title_elem:
            return None
        title = title_elem.text().strip()
        if not title or len(title) < 10:
            return None
        price_elem = element.css_first("span[class*='price']") or element.css_first("div[class*='price']") or element.css_first("span[class*='amount']")
        price = None
        if price_elem:
            price_text = price_elem.text().strip()
            price = _extract_price(price_text)
        location_elem = element.css_first("span[class*='location']") or element.css_first("div[class*='location']") or element.css_first("span[class*='area']")
        location = location_elem.text().strip() if location_elem else "Waterloo"
        link_elem = element.css_first("a")
        url = "https://offcampushousing.uwaterloo.ca"
        if link_elem:
            href = link_elem.attributes.get("href", "")
            if href:
                url = urljoin("https://offcampushousing.uwaterloo.ca", href)
        return {
            "title": title,
            "price": price,
            "location": location,
            "source": "UW Off-Campus",
            "url": url
        }
    except Exception as e:
        logger.debug(f"Error extracting UW listing: {e}")
        return None

def _extract_price(price_text: str) -> Optional[int]:
    if not price_text:
        return None
    price_text = re.sub(r'[^\d]', '', price_text)
    try:
        price = int(price_text)
        if 400 <= price <= 2000:
            return price
    except ValueError:
        pass
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