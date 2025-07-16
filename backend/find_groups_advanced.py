#!/usr/bin/env python3
"""
Advanced script to find Facebook groups using multiple approaches
"""

import asyncio
import os
import sys
import logging
import requests
from urllib.parse import quote_plus, urlencode
import re
import json

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

async def try_different_search_methods():
    """Try different methods to search for Facebook groups"""
    print("Trying different Facebook search methods...")
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    
    found_groups = []
    
    # Method 1: Try the main Facebook search
    print("\nMethod 1: Main Facebook search")
    for i, search_term in enumerate(SEARCH_TERMS[:3], 1):  # Try first 3 terms
        try:
            encoded_term = quote_plus(search_term)
            search_url = f"https://www.facebook.com/search/?q={encoded_term}&type=groups"
            
            print(f"  [{i}] Searching: {search_term}")
            print(f"      URL: {search_url}")
            
            response = requests.get(search_url, cookies=cookies, headers=headers, timeout=30)
            print(f"      Status: {response.status_code}")
            
            if response.status_code == 200:
                content = response.text
                
                # Look for group patterns
                group_patterns = [
                    r'https://www\.facebook\.com/groups/(\d+)',
                    r'/groups/(\d+)',
                    r'data-testid="group-card"[^>]*href="/groups/([^"]+)"',
                ]
                
                for pattern in group_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match and match.isdigit():
                            group_url = f"groups/{match}"
                            if group_url not in found_groups:
                                found_groups.append(group_url)
                                print(f"        Found group: {group_url}")
            
        except Exception as e:
            print(f"      Error: {e}")
        
        await asyncio.sleep(3)
    
    # Method 2: Try GraphQL API approach
    print("\nMethod 2: GraphQL API approach")
    try:
        # Try to get the GraphQL endpoint
        graphql_url = "https://www.facebook.com/api/graphql/"
        
        # This is a simplified approach - in reality, Facebook's GraphQL API is complex
        print("  Note: Facebook's GraphQL API requires specific tokens and is heavily protected")
        print("  This method would require more sophisticated implementation")
        
    except Exception as e:
        print(f"  Error: {e}")
    
    # Method 3: Try marketplace search
    print("\nMethod 3: Marketplace search")
    try:
        marketplace_url = "https://www.facebook.com/marketplace/search/?query=waterloo%20housing"
        
        print(f"  URL: {marketplace_url}")
        
        response = requests.get(marketplace_url, cookies=cookies, headers=headers, timeout=30)
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200:
            content = response.text
            print(f"  Content length: {len(content)} characters")
            
            # Look for any group references
            if 'groups' in content.lower():
                print("  Found 'groups' in content")
            
    except Exception as e:
        print(f"  Error: {e}")
    
    return found_groups

async def provide_manual_instructions():
    """Provide detailed manual search instructions"""
    print("\n" + "=" * 60)
    print("MANUAL SEARCH INSTRUCTIONS")
    print("=" * 60)
    print("Since automated search is blocked, here's how to find groups manually:")
    print()
    print("STEP 1: Search on Facebook")
    print("1. Go to Facebook.com and log in")
    print("2. In the search bar, type one of these terms:")
    for i, term in enumerate(SEARCH_TERMS, 1):
        print(f"   {i}. '{term}'")
    print()
    print("STEP 2: Find Groups")
    print("3. Click on 'Groups' in the search results")
    print("4. Look for groups related to Waterloo housing")
    print("5. Click on a group to visit it")
    print()
    print("STEP 3: Get Group Information")
    print("6. Copy the group URL from your browser")
    print("7. The URL will look like one of these:")
    print("   - https://www.facebook.com/groups/123456789012345")
    print("   - https://www.facebook.com/groups/waterloohousing")
    print("   - https://www.facebook.com/groups/uwstudentrentals")
    print()
    print("STEP 4: Extract Group ID")
    print("8. Extract the group identifier:")
    print("   - For numeric IDs: groups/123456789012345")
    print("   - For name-based: groups/waterloohousing")
    print()
    print("STEP 5: Test the Group")
    print("9. Try visiting the group URL directly")
    print("10. Check if you can see posts in the group")
    print()
    print("STEP 6: Update the Scraper")
    print("11. Once you have working group IDs, update facebook.py:")
    print("    WATERLOO_HOUSING_SOURCES = [")
    print("        'groups/YOUR_GROUP_ID_1',")
    print("        'groups/YOUR_GROUP_ID_2',")
    print("        # ... more groups")
    print("    ]")

async def suggest_alternative_approaches():
    """Suggest alternative approaches"""
    print("\n" + "=" * 60)
    print("ALTERNATIVE APPROACHES")
    print("=" * 60)
    print("Since Facebook scraping is challenging, consider these alternatives:")
    print()
    print("1. FOCUS ON OTHER SCRAPERS")
    print("   - Reddit (already working)")
    print("   - Kijiji (needs improvement)")
    print("   - Rentals.ca (needs improvement)")
    print("   - UW Off-Campus Housing (official source)")
    print()
    print("2. USE FACEBOOK MARKETPLACE")
    print("   - More accessible than groups")
    print("   - Has dedicated housing section")
    print("   - Less anti-scraping protection")
    print()
    print("3. MANUAL DATA COLLECTION")
    print("   - Join Facebook groups manually")
    print("   - Collect listings manually")
    print("   - Use as training data for other scrapers")
    print()
    print("4. OFFICIAL APIS")
    print("   - Facebook Graph API (requires app approval)")
    print("   - UW Off-Campus Housing API")
    print("   - Kijiji API (if available)")
    print()
    print("5. BROWSER AUTOMATION")
    print("   - Use Selenium or Playwright")
    print("   - More realistic browser behavior")
    print("   - Can handle JavaScript and dynamic content")

async def main():
    """Main function"""
    print("Advanced Facebook Group Finder")
    print("=" * 60)
    
    # Try different search methods
    found_groups = await try_different_search_methods()
    
    # Show results
    print(f"\n" + "=" * 60)
    print(f"RESULTS")
    print(f"=" * 60)
    print(f"Found {len(found_groups)} potential groups:")
    
    for i, group in enumerate(found_groups, 1):
        print(f"{i}. {group}")
        print(f"   URL: https://www.facebook.com/{group}")
    
    if found_groups:
        print(f"\nTo test these groups, update the WATERLOO_HOUSING_SOURCES in facebook.py:")
        print(f"WATERLOO_HOUSING_SOURCES = {found_groups}")
    else:
        print(f"\nNo groups found through automated search.")
    
    # Provide manual instructions
    await provide_manual_instructions()
    
    # Suggest alternatives
    await suggest_alternative_approaches()

if __name__ == "__main__":
    asyncio.run(main()) 