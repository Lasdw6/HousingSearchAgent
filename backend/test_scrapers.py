#!/usr/bin/env python3
"""
Test script to verify all scrapers are working properly
"""

import asyncio
import sys
import os
import logging

# Configure logging to show debug messages
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers import (
    search_kijiji,
    search_reddit,
    search_facebook,
    search_rentals_ca,
    search_uw_offcampus,
    search_google,
    search_craigslist
)

async def test_scrapers():
    """Test all scrapers with sample parameters"""
    
    # Sample search parameters
    test_params = {
        "location": "Columbia",
        "price_min": 500,
        "price_max": 1200,
        "term": "Fall",
        "stay_length": "8 months",
        "furnished": True,
        "gender": "Any",
        "lease_type": "Private"
    }
    
    print("Testing all scrapers...")
    print("=" * 50)
    
    # Test each scraper
    scrapers = [
        ("Kijiji", search_kijiji),
        ("Reddit", search_reddit),
        ("Facebook", search_facebook),
        ("Rentals.ca", search_rentals_ca),
        ("UW Off-Campus Housing", search_uw_offcampus),
        ("Google", search_google),
        ("Craigslist", search_craigslist)
    ]
    
    total_listings = 0
    
    for name, scraper_func in scrapers:
        try:
            print(f"\nTesting {name} scraper...")
            results = await scraper_func(test_params)
            print(f"✓ {name}: Found {len(results)} listings")
            
            # Show first 2 listings as examples
            for i, listing in enumerate(results[:2]):
                print(f"  {i+1}. {listing['title']} - ${listing.get('price', 'N/A')} - {listing.get('location', 'N/A')}")
            
            total_listings += len(results)
            
        except Exception as e:
            print(f"✗ {name}: Error - {e}")
    
    print("\n" + "=" * 50)
    print(f"Total listings found: {total_listings}")
    print("All scrapers tested!")

if __name__ == "__main__":
    asyncio.run(test_scrapers()) 