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

async def search_kijiji(params: Dict) -> List[Dict]:
    """
    Search Kijiji for housing listings with improved anti-bot detection
    
    Args:
        params: Search parameters including location, price range, etc.
    
    Returns:
        List of housing listings
    """
    try:
        logger.info("Searching Kijiji...")
        
        # Multiple search approaches
        search_approaches = [
            _search_kijiji_approach_1,
            _search_kijiji_approach_2,
            _search_kijiji_approach_3
        ]
        
        for approach in search_approaches:
            try:
                listings = await approach(params)
                if listings:
                    logger.info(f"Kijiji: Found {len(listings)} listings using approach {approach.__name__}")
                    return listings
            except Exception as e:
                logger.warning(f"Kijiji approach {approach.__name__} failed: {e}")
                continue
        
        logger.warning("Kijiji: All approaches failed, no listings found.")
        return []
                
    except Exception as e:
        logger.error(f"Error searching Kijiji: {e}")
        return []

async def _search_kijiji_approach_1(params: Dict) -> List[Dict]:
    """Approach 1: Direct search with rotating user agents"""
    base_url = "https://www.kijiji.ca/b-for-rent/kitchener-waterloo/"
    
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
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
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
            logger.warning(f"Kijiji approach 1 returned status {response.status_code}")
            return []
        
        return _parse_kijiji_listings(response.text, "Kijiji", params)

async def _search_kijiji_approach_2(params: Dict) -> List[Dict]:
    """Approach 2: Category-based search without query"""
    base_url = "https://www.kijiji.ca/b-for-rent/kitchener-waterloo/"
    
    # Try different category URLs
    category_urls = [
        f"{base_url}",
        f"{base_url}?sort=creationTimeDesc",
        f"{base_url}?sort=priceAsc",
        f"{base_url}?sort=priceDesc"
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
                    listings = _parse_kijiji_listings(response.text, "Kijiji", params)
                    if listings:
                        return listings
            except Exception as e:
                logger.debug(f"Kijiji approach 2 failed for {url}: {e}")
                continue
    
    return []

async def _search_kijiji_approach_3(params: Dict) -> List[Dict]:
    """Approach 3: Use mobile user agent and different headers"""
    base_url = "https://www.kijiji.ca/b-for-rent/kitchener-waterloo/"
    
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
            logger.warning(f"Kijiji approach 3 returned status {response.status_code}")
            return []
        
        return _parse_kijiji_listings(response.text, "Kijiji", params)

def _parse_kijiji_listings(html: str, source: str, params: Dict) -> List[Dict]:
    """Parse listings from Kijiji HTML"""
    try:
        parser = HTMLParser(html)
        
        # Multiple selector strategies
        selectors = [
            "div[data-testid='listing-card']",
            "div[class*='listing-card']",
            "div[class*='search-item']",
            "div[class*='ad-item']",
            "article[class*='listing']",
            "div[class*='container']",
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
        logger.error(f"Error parsing Kijiji listings: {e}")
        return []

def _extract_listing_data(element, source: str) -> Optional[Dict]:
    """Extract listing data from HTML element with improved selectors"""
    try:
        # Multiple title selectors
        title_selectors = [
            "h3[class*='title']",
            "a[class*='title']",
            "h3",
            "h2",
            "span[class*='title']",
            "div[class*='title']"
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
        
        # Multiple price selectors
        price_selectors = [
            "span[class*='price']",
            "div[class*='price']",
            "span[class*='amount']",
            "p[class*='price']",
            "span[class*='cost']",
            "div[class*='cost']"
        ]
        
        price = None
        for selector in price_selectors:
            price_elem = element.css_first(selector)
            if price_elem:
                price_text = price_elem.text().strip()
                price = _extract_price(price_text)
                if price:
                    break
        
        # Multiple location selectors
        location_selectors = [
            "span[class*='location']",
            "div[class*='location']",
            "span[class*='area']",
            "p[class*='location']",
            "span[class*='address']",
            "div[class*='address']"
        ]
        
        location = "Waterloo"
        for selector in location_selectors:
            location_elem = element.css_first(selector)
            if location_elem:
                location = location_elem.text().strip()
                break
        
        # Multiple link selectors
        link_selectors = [
            "a[href*='/v-apartments-condos/']",
            "a[href*='/v-real-estate/']",
            "a[class*='listing']",
            "a[href*='kijiji.ca']",
            "a"
        ]
        
        url = "https://kijiji.ca"
        for selector in link_selectors:
            link_elem = element.css_first(selector)
            if link_elem:
                href = link_elem.attributes.get("href", "")
                if href and "kijiji.ca" in href:
                    url = urljoin("https://kijiji.ca", href)
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