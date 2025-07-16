#!/usr/bin/env python3
"""
Script to find real Facebook groups using Facebook search
"""

import asyncio
import os
import sys
import logging
import requests
from urllib.parse import quote_plus
import re

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Search terms for Waterloo housing groups
SEARCH_TERMS = [
    "Waterloo student housing",
    "UW housing",
    "Waterloo rentals",
    "University of Waterloo housing",
    "Waterloo student accommodation",
    "UW student rentals",
    "Waterloo student housing group",
    "Kitchener Waterloo rentals",
    "Waterloo off campus housing",
    "UW off campus housing"
]

async def search_facebook_groups():
    """Search Facebook for Waterloo housing groups"""
    print("Searching Facebook for Waterloo housing groups...")
    print("=" * 60)
    
    # Set up cookies
    cookies_str = "c_user=100041694502927; xs=10%3ARNekcRU1BrqC6g%3A2%3A1752262070%3A-1%3A-1%3A%3AAcULfA9c9VIhI5PaJptFxPgYc2hfkunAA6SstNCZfA; datr=4CLQZvG8o8ZgHFphcrXHwulc; sb=S4oDZ-WL_4NuKpdWhnnVOtPD"
    
    # Parse cookies
    cookies = {}
    for cookie in cookies_str.split(';'):
        if '=' in cookie:
            name, value = cookie.strip().split('=', 1)
            cookies[name] = value
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    found_groups = []
    
    for i, search_term in enumerate(SEARCH_TERMS, 1):
        print(f"\n[{i}/{len(SEARCH_TERMS)}] Searching for: '{search_term}'")
        
        try:
            # URL encode the search term
            encoded_term = quote_plus(search_term)
            search_url = f"https://www.facebook.com/search/groups/?q={encoded_term}"
            
            print(f"  URL: {search_url}")
            
            # Make the request
            response = requests.get(search_url, cookies=cookies, headers=headers, timeout=30)
            
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                # Look for group URLs in the response
                content = response.text
                
                # Find group URLs using regex
                group_patterns = [
                    r'https://www\.facebook\.com/groups/(\d+)',  # Group ID
                    r'https://www\.facebook\.com/groups/([^/"]+)',  # Group name
                    r'/groups/(\d+)',  # Just group ID
                    r'/groups/([^/"]+)',  # Just group name
                ]
                
                for pattern in group_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match and match not in ['groups', 'search', 'category']:
                            group_url = f"groups/{match}"
                            if group_url not in found_groups:
                                found_groups.append(group_url)
                                print(f"    Found group: {group_url}")
                
                # Also look for group names in the HTML
                group_name_pattern = r'<a[^>]*href="/groups/[^"]*"[^>]*>([^<]+)</a>'
                name_matches = re.findall(group_name_pattern, content)
                for name in name_matches:
                    if 'waterloo' in name.lower() or 'uw' in name.lower() or 'housing' in name.lower():
                        print(f"    Found group name: {name}")
                
            else:
                print(f"  Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Error searching for '{search_term}': {e}")
        
        # Small delay between requests
        await asyncio.sleep(2)
    
    print(f"\n" + "=" * 60)
    print(f"SUMMARY")
    print(f"=" * 60)
    print(f"Found {len(found_groups)} potential groups:")
    
    for i, group in enumerate(found_groups, 1):
        print(f"{i}. {group}")
        print(f"   URL: https://www.facebook.com/{group}")
    
    if found_groups:
        print(f"\nTo test these groups, update the WATERLOO_HOUSING_SOURCES in facebook.py:")
        print(f"WATERLOO_HOUSING_SOURCES = {found_groups}")
    else:
        print(f"\nNo groups found. You may need to:")
        print(f"1. Search manually on Facebook")
        print(f"2. Join some Waterloo housing groups")
        print(f"3. Get group IDs from the URL when you visit groups")

async def test_manual_search():
    """Provide instructions for manual search"""
    print("\n" + "=" * 60)
    print("MANUAL SEARCH INSTRUCTIONS")
    print("=" * 60)
    print("Since automated search may be blocked, here's how to find groups manually:")
    print()
    print("1. Go to Facebook.com and log in")
    print("2. In the search bar, type one of these terms:")
    for term in SEARCH_TERMS:
        print(f"   - '{term}'")
    print()
    print("3. Click on 'Groups' in the search results")
    print("4. Look for groups related to Waterloo housing")
    print("5. Click on a group to visit it")
    print("6. Copy the group URL (it will look like: https://www.facebook.com/groups/123456789012345)")
    print("7. Extract the group ID (the number after /groups/)")
    print()
    print("Common group URL patterns:")
    print("- https://www.facebook.com/groups/123456789012345 (numeric ID)")
    print("- https://www.facebook.com/groups/waterloohousing (name-based)")
    print()
    print("Once you have group IDs, update the facebook.py scraper with real group IDs.")

async def main():
    """Main function"""
    print("Facebook Group Finder")
    print("=" * 60)
    
    # Try automated search first
    await search_facebook_groups()
    
    # Provide manual search instructions
    await test_manual_search()

if __name__ == "__main__":
    asyncio.run(main()) 