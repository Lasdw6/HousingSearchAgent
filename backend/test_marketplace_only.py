#!/usr/bin/env python3
"""
Test script for Facebook Marketplace only
"""

import asyncio
import os
import sys
import logging

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.facebook import search_facebook

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_marketplace_only():
    """Test Facebook Marketplace only"""
    print("Testing Facebook Marketplace only...")
    print("=" * 60)
    
    # Set up cookies
    os.environ['FACEBOOK_COOKIES'] = "c_user=100041694502927; xs=10%3ARNekcRU1BrqC6g%3A2%3A1752262070%3A-1%3A-1%3A%3AAcULfA9c9VIhI5PaJptFxPgYc2hfkunAA6SstNCZfA; datr=4CLQZvG8o8ZgHFphcrXHwulc; sb=S4oDZ-WL_4NuKpdWhnnVOtPD"
    
    test_params = {
        "location": "Waterloo",
        "price_min": 500,
        "price_max": 1200,
        "term": "Fall",
        "stay_length": "8 months",
        "furnished": True,
        "gender": "Any",
        "lease_type": "Private"
    }
    
    try:
        # Temporarily modify the sources to test only Marketplace
        import app.scrapers.facebook as fb_module
        original_sources = fb_module.WATERLOO_HOUSING_SOURCES.copy()
        fb_module.WATERLOO_HOUSING_SOURCES = [
            "marketplace/search",
            "marketplace/category/housing",
            "marketplace/category/real-estate",
        ]
        
        results = await search_facebook(test_params)
        
        print(f"Marketplace results: {len(results)} listings found")
        
        if results:
            for i, listing in enumerate(results[:5], 1):
                print(f"{i}. {listing.get('title', 'No title')}")
                print(f"   Price: ${listing.get('price', 'N/A')}")
                print(f"   Location: {listing.get('location', 'N/A')}")
                print(f"   Source: {listing.get('source', 'Unknown')}")
                print(f"   Score: {listing.get('score', 0)}")
                print()
        else:
            print("No listings found from Marketplace")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Restore original sources
    fb_module.WATERLOO_HOUSING_SOURCES = original_sources

async def main():
    """Main test function"""
    print("Facebook Marketplace Testing")
    print("=" * 60)
    await test_marketplace_only()

if __name__ == "__main__":
    asyncio.run(main()) 