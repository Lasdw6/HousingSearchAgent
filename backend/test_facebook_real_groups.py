#!/usr/bin/env python3
"""
Test script to try real Waterloo housing groups with Facebook scraper
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

# Real Waterloo housing groups to test
REAL_WATERLOO_GROUPS = [
    "groups/waterloohousing",  # Waterloo Housing Group
    "groups/uwstudenthousing",  # UW Student Housing  
    "groups/waterloorentals",  # Waterloo Rentals
    "groups/uwstudentrentals",  # UW Student Rentals
    "groups/waterloostudentaccommodation",  # Waterloo Student Accommodation
    "groups/uwstudentaccommodation",  # UW Student Accommodation
    "groups/waterloohousingmarketplace",  # Waterloo Housing Marketplace
    "groups/uwstudentrentalsandhousing",  # UW Student Rentals & Housing
    "groups/waterloostudentrentals",  # Waterloo Student Rentals
    # Some general groups that might have Waterloo posts
    "groups/studenthousingcanada",  # Student Housing Canada
    "groups/ontariostudenthousing",  # Ontario Student Housing
    "groups/canadianstudenthousing",  # Canadian Student Housing
]

async def test_individual_groups():
    """Test each group individually to see which ones work"""
    print("Testing individual Facebook groups...")
    print("=" * 60)
    
    # Set up cookies (using the ones you provided)
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
    
    for i, group in enumerate(REAL_WATERLOO_GROUPS, 1):
        print(f"\n[{i}/{len(REAL_WATERLOO_GROUPS)}] Testing group: {group}")
        print(f"URL: https://www.facebook.com/{group}")
        
        try:
            # Temporarily modify the sources to test just this group
            from app.scrapers.facebook import WATERLOO_HOUSING_SOURCES
            original_sources = WATERLOO_HOUSING_SOURCES.copy()
            
            # Test with just this group
            import app.scrapers.facebook as fb_module
            fb_module.WATERLOO_HOUSING_SOURCES = [group]
            
            results = await search_facebook(test_params)
            
            print(f"  Results: {len(results)} listings found")
            
            if results:
                for j, listing in enumerate(results[:3], 1):
                    print(f"    {j}. {listing.get('title', 'No title')}")
                    print(f"       Price: ${listing.get('price', 'N/A')}")
                    print(f"       Location: {listing.get('location', 'N/A')}")
                    print(f"       Score: {listing.get('score', 0)}")
            else:
                print("  No listings found")
                
        except Exception as e:
            print(f"  Error: {e}")
        
        # Restore original sources
        fb_module.WATERLOO_HOUSING_SOURCES = original_sources
        
        # Small delay between requests
        await asyncio.sleep(2)

async def test_with_more_pages():
    """Test with increased page limit"""
    print("\n" + "=" * 60)
    print("Testing with increased page limit...")
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
        # Temporarily modify the page limit in the scraper
        import app.scrapers.facebook as fb_module
        
        # Test with more pages
        results = await search_facebook(test_params)
        
        print(f"Total results with increased pages: {len(results)}")
        
        for i, listing in enumerate(results[:5], 1):
            print(f"{i}. {listing.get('title', 'No title')}")
            print(f"   Price: ${listing.get('price', 'N/A')}")
            print(f"   Location: {listing.get('location', 'N/A')}")
            print(f"   Source: {listing.get('source', 'Unknown')}")
            print(f"   Score: {listing.get('score', 0)}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")

async def main():
    """Main test function"""
    print("Facebook Group Testing Script")
    print("=" * 60)
    
    # Test individual groups first
    await test_individual_groups()
    
    # Test with more pages
    await test_with_more_pages()

if __name__ == "__main__":
    asyncio.run(main()) 