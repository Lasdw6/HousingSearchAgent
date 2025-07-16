#!/usr/bin/env python3
"""
Test script for Google Playwright scraper
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.google_playwright import search_google_playwright

async def test_google_playwright():
    """Test the Google Playwright scraper"""
    print("🧪 Testing Google Playwright Scraper")
    print("=" * 50)
    
    # Test parameters
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
    
    print(f"Search parameters: {test_params}")
    print("\n🔍 Starting Google search...")
    
    try:
        results = await search_google_playwright(test_params)
        
        print(f"\n✅ Search completed!")
        print(f"📊 Found {len(results)} listings")
        
        if results:
            print("\n📋 Sample results:")
            for i, listing in enumerate(results[:5], 1):
                print(f"\n{i}. {listing['title']}")
                print(f"   💰 Price: ${listing.get('price', 'N/A')}")
                print(f"   📍 Location: {listing.get('location', 'N/A')}")
                print(f"   🔗 Source: {listing['source']}")
                print(f"   🌐 URL: {listing['url']}")
        else:
            print("\n❌ No listings found")
            
    except Exception as e:
        print(f"\n❌ Error during search: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_google_playwright()) 