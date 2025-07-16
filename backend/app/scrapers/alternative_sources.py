import httpx
import asyncio
from typing import List, Dict, Optional
from selectolax.parser import HTMLParser
import re
from urllib.parse import urljoin, quote
import logging
import random
import time
import json

logger = logging.getLogger(__name__)

async def search_alternative_sources(params: Dict) -> List[Dict]:
    """
    Search alternative housing sources that are less likely to block scrapers
    
    Args:
        params: Search parameters including location, price range, etc.
    
    Returns:
        List of housing listings
    """
    try:
        logger.info("Searching alternative housing sources...")
        
        # Try multiple alternative sources
        sources = [
            _search_rentfaster,
            _search_rentboard,
            _search_rentseeker,
            _search_apartments_com
        ]
        
        all_listings = []
        for source_func in sources:
            try:
                listings = await source_func(params)
                if listings:
                    all_listings.extend(listings)
                    logger.info(f"Alternative source {source_func.__name__}: Found {len(listings)} listings")
            except Exception as e:
                logger.warning(f"Alternative source {source_func.__name__} failed: {e}")
                continue
        
        if all_listings:
            logger.info(f"Alternative sources: Found {len(all_listings)} total listings")
            return all_listings
        else:
            logger.warning("Alternative sources: No listings found.")
            return []
                
    except Exception as e:
        logger.error(f"Error searching alternative sources: {e}")
        return []

async def _search_rentfaster(params: Dict) -> List[Dict]:
    """Search RentFaster.ca - Canadian rental listings"""
    try:
        base_url = "https://www.rentfaster.ca/on/waterloo-region"
        
        search_terms = []
        if params.get("location"):
            search_terms.append(params["location"])
        if params.get("term"):
            search_terms.append(params["term"])
        
        search_terms.extend(["student", "housing"])
        query = " ".join(search_terms)
        
        url = f"{base_url}?query={quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
        
        await asyncio.sleep(random.uniform(1, 2))
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return []
            
            return _parse_rentfaster_listings(response.text, "RentFaster", params)
            
    except Exception as e:
        logger.debug(f"RentFaster search failed: {e}")
        return []

async def _search_rentboard(params: Dict) -> List[Dict]:
    """Search RentBoard.ca - Canadian rental listings"""
    try:
        base_url = "https://www.rentboard.ca/on/waterloo"
        
        search_terms = []
        if params.get("location"):
            search_terms.append(params["location"])
        
        search_terms.extend(["student", "housing"])
        query = " ".join(search_terms)
        
        url = f"{base_url}?search={quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        await asyncio.sleep(random.uniform(1, 2))
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return []
            
            return _parse_rentboard_listings(response.text, "RentBoard", params)
            
    except Exception as e:
        logger.debug(f"RentBoard search failed: {e}")
        return []

async def _search_rentseeker(params: Dict) -> List[Dict]:
    """Search RentSeeker.ca - Canadian rental listings"""
    try:
        base_url = "https://www.rentseeker.ca/on/waterloo"
        
        search_terms = []
        if params.get("location"):
            search_terms.append(params["location"])
        
        search_terms.extend(["student", "housing"])
        query = " ".join(search_terms)
        
        url = f"{base_url}?q={quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        await asyncio.sleep(random.uniform(1, 2))
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return []
            
            return _parse_rentseeker_listings(response.text, "RentSeeker", params)
            
    except Exception as e:
        logger.debug(f"RentSeeker search failed: {e}")
        return []

async def _search_apartments_com(params: Dict) -> List[Dict]:
    """Search Apartments.com - US site but sometimes has Canadian listings"""
    try:
        base_url = "https://www.apartments.com/waterloo-on/"
        
        search_terms = []
        if params.get("location"):
            search_terms.append(params["location"])
        
        search_terms.extend(["student", "housing"])
        query = " ".join(search_terms)
        
        url = f"{base_url}?search={quote(query)}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        }
        
        await asyncio.sleep(random.uniform(1, 2))
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                return []
            
            return _parse_apartments_com_listings(response.text, "Apartments.com", params)
            
    except Exception as e:
        logger.debug(f"Apartments.com search failed: {e}")
        return []

def _parse_rentfaster_listings(html: str, source: str, params: Dict) -> List[Dict]:
    """Parse listings from RentFaster HTML"""
    try:
        parser = HTMLParser(html)
        
        selectors = [
            "div[class*='listing']",
            "div[class*='property']",
            "div[class*='item']",
            "article[class*='listing']"
        ]
        
        listings = []
        for selector in selectors:
            elements = parser.css(selector)
            if elements:
                for element in elements[:20]:
                    listing = _extract_listing_data(element, source)
                    if listing and _matches_filters(listing, params):
                        listings.append(listing)
                
                if listings:
                    break
        
        return listings
        
    except Exception as e:
        logger.debug(f"Error parsing RentFaster listings: {e}")
        return []

def _parse_rentboard_listings(html: str, source: str, params: Dict) -> List[Dict]:
    """Parse listings from RentBoard HTML"""
    try:
        parser = HTMLParser(html)
        
        selectors = [
            "div[class*='listing']",
            "div[class*='property']",
            "div[class*='item']",
            "article[class*='listing']"
        ]
        
        listings = []
        for selector in selectors:
            elements = parser.css(selector)
            if elements:
                for element in elements[:20]:
                    listing = _extract_listing_data(element, source)
                    if listing and _matches_filters(listing, params):
                        listings.append(listing)
                
                if listings:
                    break
        
        return listings
        
    except Exception as e:
        logger.debug(f"Error parsing RentBoard listings: {e}")
        return []

def _parse_rentseeker_listings(html: str, source: str, params: Dict) -> List[Dict]:
    """Parse listings from RentSeeker HTML"""
    try:
        parser = HTMLParser(html)
        
        selectors = [
            "div[class*='listing']",
            "div[class*='property']",
            "div[class*='item']",
            "article[class*='listing']"
        ]
        
        listings = []
        for selector in selectors:
            elements = parser.css(selector)
            if elements:
                for element in elements[:20]:
                    listing = _extract_listing_data(element, source)
                    if listing and _matches_filters(listing, params):
                        listings.append(listing)
                
                if listings:
                    break
        
        return listings
        
    except Exception as e:
        logger.debug(f"Error parsing RentSeeker listings: {e}")
        return []

def _parse_apartments_com_listings(html: str, source: str, params: Dict) -> List[Dict]:
    """Parse listings from Apartments.com HTML"""
    try:
        parser = HTMLParser(html)
        
        selectors = [
            "div[class*='listing']",
            "div[class*='property']",
            "div[class*='item']",
            "article[class*='listing']"
        ]
        
        listings = []
        for selector in selectors:
            elements = parser.css(selector)
            if elements:
                for element in elements[:20]:
                    listing = _extract_listing_data(element, source)
                    if listing and _matches_filters(listing, params):
                        listings.append(listing)
                
                if listings:
                    break
        
        return listings
        
    except Exception as e:
        logger.debug(f"Error parsing Apartments.com listings: {e}")
        return []

def _extract_listing_data(element, source: str) -> Optional[Dict]:
    """Extract listing data from HTML element with generic selectors"""
    try:
        # Generic title selectors
        title_selectors = [
            "h3",
            "h2",
            "h4",
            "span[class*='title']",
            "div[class*='title']",
            "a[class*='title']",
            "span[class*='name']",
            "div[class*='name']"
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
        
        # Generic price selectors
        price_selectors = [
            "span[class*='price']",
            "div[class*='price']",
            "span[class*='amount']",
            "p[class*='price']",
            "span[class*='cost']",
            "div[class*='cost']",
            "span[class*='rent']",
            "div[class*='rent']"
        ]
        
        price = None
        for selector in price_selectors:
            price_elem = element.css_first(selector)
            if price_elem:
                price_text = price_elem.text().strip()
                price = _extract_price(price_text)
                if price:
                    break
        
        # Generic location selectors
        location_selectors = [
            "span[class*='location']",
            "div[class*='location']",
            "span[class*='area']",
            "p[class*='location']",
            "span[class*='address']",
            "div[class*='address']",
            "span[class*='city']",
            "div[class*='city']"
        ]
        
        location = "Waterloo"
        for selector in location_selectors:
            location_elem = element.css_first(selector)
            if location_elem:
                location = location_elem.text().strip()
                break
        
        # Generic link selectors
        link_selectors = [
            "a[href*='rent']",
            "a[href*='property']",
            "a[href*='listing']",
            "a[class*='listing']",
            "a"
        ]
        
        url = f"https://{source.lower().replace('.com', '').replace('.ca', '')}.com"
        for selector in link_selectors:
            link_elem = element.css_first(selector)
            if link_elem:
                href = link_elem.attributes.get("href", "")
                if href:
                    url = urljoin(url, href)
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