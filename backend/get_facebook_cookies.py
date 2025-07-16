#!/usr/bin/env python3
"""
Script to help get Facebook session cookies and test the Facebook scraper
"""

import os
import asyncio
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.scrapers.facebook import search_facebook

def print_instructions():
    """Print instructions for getting Facebook cookies"""
    print("=" * 60)
    print("FACEBOOK SESSION COOKIES SETUP")
    print("=" * 60)
    print()
    print("To access Facebook groups, you need to provide session cookies.")
    print("Here's how to get them:")
    print()
    print("1. Open your web browser and go to Facebook.com")
    print("2. Log in to your Facebook account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to the 'Application' or 'Storage' tab")
    print("5. Look for 'Cookies' in the left sidebar")
    print("6. Click on 'https://www.facebook.com'")
    print("7. Find these important cookies:")
    print("   - c_user")
    print("   - xs")
    print("   - datr")
    print("   - sb")
    print("8. Copy their values")
    print()
    print("Then set the environment variable:")
    print("export FACEBOOK_COOKIES='c_user=YOUR_VALUE; xs=YOUR_VALUE; datr=YOUR_VALUE; sb=YOUR_VALUE'")
    print()
    print("Or on Windows:")
    print("set FACEBOOK_COOKIES=c_user=YOUR_VALUE; xs=YOUR_VALUE; datr=YOUR_VALUE; sb=YOUR_VALUE")
    print()
    print("WARNING: Keep your cookies secure and don't share them!")
    print("=" * 60)

async def test_facebook_scraper():
    """Test the Facebook scraper with sample parameters"""
    print("Testing Facebook scraper...")
    print()
    
    # Sample search parameters
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
        results = await search_facebook(test_params)
        print(f"Found {len(results)} Facebook listings")
        
        for i, listing in enumerate(results[:5], 1):
            print(f"{i}. {listing.get('title', 'No title')}")
            print(f"   Price: ${listing.get('price', 'N/A')}")
            print(f"   Location: {listing.get('location', 'N/A')}")
            print(f"   Source: {listing.get('source', 'Unknown')}")
            print(f"   Score: {listing.get('score', 0)}")
            print()
            
    except Exception as e:
        print(f"Error testing Facebook scraper: {e}")

def main():
    """Main function"""
    print_instructions()
    
    # Check if cookies are set
    cookies = os.getenv('FACEBOOK_COOKIES')
    if not cookies:
        print("No Facebook cookies found in environment variables.")
        print("Please set FACEBOOK_COOKIES environment variable first.")
        return
    
    print("Facebook cookies found! Testing scraper...")
    print()
    
    # Test the scraper
    asyncio.run(test_facebook_scraper())

if __name__ == "__main__":
    main() 