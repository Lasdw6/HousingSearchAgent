#!/usr/bin/env python3
"""
Test script for more realistic Facebook group names
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

# More realistic group names that are likely to exist
REALISTIC_GROUPS = [
    "groups/waterloostudenthousing",  # More likely name
    "groups/uwstudentrentals",  # UW student rentals
    "groups/waterloorentals",  # Waterloo rentals
    "groups/kitchenerwaterloorentals",  # Kitchener-Waterloo rentals
    "groups/uwstudentaccommodation",  # UW accommodation
    "groups/waterloostudentrentals",  # Waterloo student rentals
    "groups/uwstudentrentalsandhousing",  # UW rentals and housing
    "groups/waterloostudentaccommodation",  # Waterloo student accommodation
    # Some general groups that might have Waterloo posts
    "groups/studenthousingcanada",  # Student Housing Canada
    "groups/ontariostudenthousing",  # Ontario Student Housing
    "groups/canadianstudenthousing",  # Canadian Student Housing
    # Try some variations
    "groups/waterloohousing",  # Simple Waterloo housing
    "groups/uwhousing",  # Simple UW housing
    "groups/waterloostudents",  # Waterloo students
    "groups/uwstudents",  # UW students
]

async def test_realistic_groups():
    """Test more realistic group names"""
    print("Testing realistic Facebook group names...")
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
    
    for i, group in enumerate(REALISTIC_GROUPS, 1):
        print(f"\n[{i}/{len(REALISTIC_GROUPS)}] Testing group: {group}")
        print(f"URL: https://www.facebook.com/{group}")
        
        try:
            # Temporarily modify the sources to test just this group
            import app.scrapers.facebook as fb_module
            original_sources = fb_module.WATERLOO_HOUSING_SOURCES.copy()
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

async def main():
    """Main test function"""
    print("Realistic Facebook Group Testing")
    print("=" * 60)
    await test_realistic_groups()

if __name__ == "__main__":
    asyncio.run(main()) 