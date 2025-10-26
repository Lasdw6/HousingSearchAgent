import httpx
import asyncio
from typing import List, Dict, Optional
from selectolax.parser import HTMLParser
import re
from urllib.parse import urljoin, quote
import logging
import random
import time

logger = logging.getLogger(__name__)

async def search_craigslist(params: Dict) -> List[Dict]:
    """
    Search Craigslist for housing listings with improved anti-bot detection
    
    Args:
        params: Search parameters including location, price range, etc.
    
    Returns:
        List of housing listings
    """
    try:
        logger.info("Searching Craigslist...")
        
        # Multiple search approaches
        search_approaches = [
            _search_craigslist_approach_1,
            _search_craigslist_approach_2,
            _search_craigslist_approach_3
        ]
        
        for approach in search_approaches:
            try:
                listings = await approach(params)
                if listings:
                    logger.info(f"Craigslist: Found {len(listings)} listings using approach {approach.__name__}")
                    return listings
            except Exception as e:
                logger.warning(f"Craigslist approach {approach.__name__} failed: {e}")
                continue
        
        logger.warning("Craigslist: All approaches failed, no listings found.")
        return []
                
    except Exception as e:
        logger.error(f"Error searching Craigslist: {e}")
        return []

async def _search_craigslist_approach_1(params: Dict) -> List[Dict]:
    """Approach 1: Direct search with rotating user agents"""
    base_url = "https://kitchener.craigslist.org/search/apa"
    
    # Build search terms
    search_terms = []
    if params.get("location"):
        search_terms.append(params["location"])
    if params.get("term"):
        search_terms.append(params["term"])
    
    search_terms.extend(["student", "housing", "rent"])
    query = " ".join(search_terms)
    
    url = f"{base_url}?query={quote(query)}"
    
    # Rotating user agents
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }
    
    # Add random delay
    await asyncio.sleep(random.uniform(1, 3))
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.warning(f"Craigslist approach 1 returned status {response.status_code}")
            return []
        
        return _parse_craigslist_listings(response.text, "Craigslist", params)

async def _search_craigslist_approach_2(params: Dict) -> List[Dict]:
    """Approach 2: Category-based search without query"""
    base_url = "https://kitchener.craigslist.org/search/apa"
    
    # Try different category URLs
    category_urls = [
        f"{base_url}",
        f"{base_url}?sort=date",
        f"{base_url}?sort=rel",
        f"{base_url}?sort=priceasc",
        f"{base_url}?sort=pricedsc"
    ]
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    await asyncio.sleep(random.uniform(2, 4))
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        for url in category_urls:
            try:
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    listings = _parse_craigslist_listings(response.text, "Craigslist", params)
                    if listings:
                        return listings
            except Exception as e:
                logger.debug(f"Craigslist approach 2 failed for {url}: {e}")
                continue
    
    return []

async def _search_craigslist_approach_3(params: Dict) -> List[Dict]:
    """Approach 3: Use mobile user agent and different headers"""
    base_url = "https://kitchener.craigslist.org/search/apa"
    
    search_terms = []
    if params.get("location"):
        search_terms.append(params["location"])
    
    search_terms.extend(["student", "housing"])
    query = " ".join(search_terms)
    
    url = f"{base_url}?query={quote(query)}"
    
    # Mobile user agent
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    await asyncio.sleep(random.uniform(3, 5))
    
    async with httpx.AsyncClient(follow_redirects=True) as client:
        response = await client.get(url, headers=headers)
        
        if response.status_code != 200:
            logger.warning(f"Craigslist approach 3 returned status {response.status_code}")
            return []
        
        return _parse_craigslist_listings(response.text, "Craigslist", params)

def _parse_craigslist_listings(html: str, source: str, params: Dict) -> List[Dict]:
    """Parse listings from Craigslist HTML"""
    try:
        parser = HTMLParser(html)
        
        # Multiple selector strategies for Craigslist
        selectors = [
            "li[class*='result-row']",
            "div[class*='result-row']",
            "li[class*='listing']",
            "div[class*='listing']",
            "li[class*='item']",
            "div[class*='item']"
        ]
        
        listings = []
        for selector in selectors:
            elements = parser.css(selector)
            if elements:
                for element in elements[:30]:  # Increased limit
                    listing = _extract_listing_data(element, source)
                    if listing and _matches_filters(listing, params):
                        listings.append(listing)
                
                if listings:
                    break
        
        return listings
        
    except Exception as e:
        logger.error(f"Error parsing Craigslist listings: {e}")
        return []

def _extract_listing_data(element, source: str) -> Optional[Dict]:
    """Extract listing data from Craigslist HTML element"""
    try:
        # Multiple title selectors for Craigslist
        title_selectors = [
            "a[class*='result-title']",
            "h3[class*='result-heading']",
            "a[class*='title']",
            "h3",
            "h2",
            "a"
        ]
        
        title_elem = None
        for selector in title_selectors:
            title_elem = element.css_first(selector)
            if title_elem:
                break
        
        if not title_elem:
            return None
                    
        title = title_elem.text().strip()
        if not title or len(title) < 5:
            return None
        
        # Multiple price selectors for Craigslist
        price_selectors = [
            "span[class*='result-price']",
            "span[class*='price']",
            "div[class*='price']",
            "span[class*='amount']",
            "p[class*='price']"
        ]
        
        price = None
        for selector in price_selectors:
            price_elem = element.css_first(selector)
            if price_elem:
                price_text = price_elem.text().strip()
                price = _extract_price(price_text)
                if price:
                    break
        
        # Multiple location selectors for Craigslist
        location_selectors = [
            "span[class*='result-hood']",
            "span[class*='location']",
            "div[class*='location']",
            "span[class*='area']",
            "p[class*='location']"
        ]
        
        location = "Kitchener-Waterloo"
        for selector in location_selectors:
            location_elem = element.css_first(selector)
            if location_elem:
                location = location_elem.text().strip()
                break
        
        # Multiple link selectors for Craigslist
        link_selectors = [
            "a[class*='result-title']",
            "a[class*='title']",
            "a[href*='craigslist.org']",
            "a"
        ]
        
        url = "https://kitchener.craigslist.org"
        for selector in link_selectors:
            link_elem = element.css_first(selector)
            if link_elem:
                href = link_elem.attributes.get("href", "")
                if href and "craigslist.org" in href:
                    url = urljoin("https://kitchener.craigslist.org", href)
                    break
        
        return {
            "title": title,
            "price": price,
            "location": location,
            "source": source,
            "url": url
        }
            
    except Exception as e:
        logger.debug(f"Error extracting listing data: {e}")
        return None

def _extract_price(price_text: str) -> Optional[int]:
    """Extract price from text with improved parsing"""
    if not price_text:
        return None
    
    # Remove common text and symbols, but keep decimal points
    price_text = re.sub(r'[^\d.]', '', price_text)
    
    try:
        # Handle decimal prices
        if '.' in price_text:
            price = float(price_text)
            price = int(price)
        else:
            price = int(price_text)
        
        if 300 <= price <= 3000:  # Wider range for student housing
            return price
    except ValueError:
        pass
    
    return None

def _matches_filters(listing: Dict, params: Dict) -> bool:
    """Check if listing matches user filters"""
    # Price filter
    if listing.get("price"):
        price = listing["price"]
        if params.get("price_min") and price < params["price_min"]:
            return False
        if params.get("price_max") and price > params["price_max"]:
            return False
    
    # Location filter
    if params.get("location"):
        location = params["location"].lower()
        listing_location = listing.get("location", "").lower()
        listing_title = listing.get("title", "").lower()
        
        if location not in listing_location and location not in listing_title:
            return False
    
    return True 