#!/usr/bin/env python3
"""
Script to parse Facebook search results and extract group information
"""

import asyncio
import os
import sys
import logging
import requests
from urllib.parse import quote_plus
import re
import json
from bs4 import BeautifulSoup

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def parse_facebook_search_results():
    """Parse Facebook search results to find groups"""
    print("Parsing Facebook search results...")
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
    
    # Search terms to try
    search_terms = [
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
    
    for i, search_term in enumerate(search_terms, 1):
        print(f"\n[{i}/{len(search_terms)}] Searching for: '{search_term}'")
        
        try:
            # URL encode the search term
            encoded_term = quote_plus(search_term)
            search_url = f"https://www.facebook.com/search/?q={encoded_term}&type=groups"
            
            print(f"  URL: {search_url}")
            
            # Make the request
            response = requests.get(search_url, cookies=cookies, headers=headers, timeout=30)
            
            print(f"  Status: {response.status_code}")
            print(f"  Content length: {len(response.text)} characters")
            
            if response.status_code == 200:
                content = response.text
                
                # Save the HTML content for debugging
                with open(f"facebook_search_{i}.html", "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"  Saved HTML to facebook_search_{i}.html")
                
                # Parse with BeautifulSoup
                soup = BeautifulSoup(content, 'html.parser')
                
                # Look for group links
                group_links = soup.find_all('a', href=re.compile(r'/groups/'))
                
                print(f"  Found {len(group_links)} group links")
                
                for link in group_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Extract group ID from href
                    group_match = re.search(r'/groups/([^/?]+)', href)
                    if group_match:
                        group_id = group_match.group(1)
                        
                        # Skip if it's just "groups" or other non-group content
                        if group_id and group_id not in ['groups', 'search', 'category', '']:
                            group_url = f"groups/{group_id}"
                            
                            if group_url not in found_groups:
                                found_groups.append(group_url)
                                print(f"    Found group: {group_url}")
                                print(f"      Text: {text[:100]}...")
                                print(f"      Full href: {href}")
                
                # Also look for any script tags that might contain group data
                scripts = soup.find_all('script')
                for script in scripts:
                    script_content = script.string
                    if script_content:
                        # Look for group IDs in script content
                        group_matches = re.findall(r'"group_id":"(\d+)"', script_content)
                        for group_id in group_matches:
                            group_url = f"groups/{group_id}"
                            if group_url not in found_groups:
                                found_groups.append(group_url)
                                print(f"    Found group in script: {group_url}")
                
                # Look for any JSON data
                json_matches = re.findall(r'\{[^{}]*"group_id"[^{}]*\}', content)
                for json_str in json_matches:
                    try:
                        data = json.loads(json_str)
                        if 'group_id' in data:
                            group_id = data['group_id']
                            group_url = f"groups/{group_id}"
                            if group_url not in found_groups:
                                found_groups.append(group_url)
                                print(f"    Found group in JSON: {group_url}")
                    except json.JSONDecodeError:
                        pass
                
            else:
                print(f"  Error: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"  Error searching for '{search_term}': {e}")
        
        # Small delay between requests
        await asyncio.sleep(3)
    
    return found_groups

async def analyze_saved_files():
    """Analyze the saved HTML files for group information"""
    print("\n" + "=" * 60)
    print("ANALYZING SAVED HTML FILES")
    print("=" * 60)
    
    found_groups = []
    
    for i in range(1, 11):  # Check files 1-10
        filename = f"facebook_search_{i}.html"
        
        if os.path.exists(filename):
            print(f"\nAnalyzing {filename}...")
            
            try:
                with open(filename, "r", encoding="utf-8") as f:
                    content = f.read()
                
                print(f"  File size: {len(content)} characters")
                
                # Look for group patterns
                group_patterns = [
                    r'https://www\.facebook\.com/groups/(\d+)',
                    r'/groups/(\d+)',
                    r'"group_id":"(\d+)"',
                    r'data-testid="group-card"[^>]*href="/groups/([^"]+)"',
                    r'<a[^>]*href="/groups/([^"]+)"[^>]*>',
                ]
                
                for pattern in group_patterns:
                    matches = re.findall(pattern, content)
                    for match in matches:
                        if match and match.isdigit():
                            group_url = f"groups/{match}"
                            if group_url not in found_groups:
                                found_groups.append(group_url)
                                print(f"    Found group: {group_url}")
                
                # Look for group names
                group_name_pattern = r'<a[^>]*href="/groups/[^"]*"[^>]*>([^<]+)</a>'
                name_matches = re.findall(group_name_pattern, content)
                for name in name_matches:
                    if 'waterloo' in name.lower() or 'uw' in name.lower() or 'housing' in name.lower():
                        print(f"    Found group name: {name}")
                
            except Exception as e:
                print(f"  Error analyzing {filename}: {e}")
    
    return found_groups

async def main():
    """Main function"""
    print("Facebook Search Parser")
    print("=" * 60)
    
    # Parse search results
    found_groups = await parse_facebook_search_results()
    
    # Analyze saved files
    additional_groups = await analyze_saved_files()
    
    # Combine results
    all_groups = list(set(found_groups + additional_groups))
    
    # Show results
    print(f"\n" + "=" * 60)
    print(f"FINAL RESULTS")
    print(f"=" * 60)
    print(f"Found {len(all_groups)} potential groups:")
    
    for i, group in enumerate(all_groups, 1):
        print(f"{i}. {group}")
        print(f"   URL: https://www.facebook.com/{group}")
    
    if all_groups:
        print(f"\nTo test these groups, update the WATERLOO_HOUSING_SOURCES in facebook.py:")
        print(f"WATERLOO_HOUSING_SOURCES = {all_groups}")
        
        # Create a test script for these groups
        print(f"\nCreating test script for found groups...")
        await create_test_script(all_groups)
    else:
        print(f"\nNo groups found. You may need to:")
        print(f"1. Search manually on Facebook")
        print(f"2. Join some Waterloo housing groups")
        print(f"3. Get group IDs from the URL when you visit groups")

async def create_test_script(groups):
    """Create a test script for the found groups"""
    script_content = f'''#!/usr/bin/env python3
"""
Test script for found Facebook groups
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

# Found groups from search
FOUND_GROUPS = {groups}

async def test_found_groups():
    """Test the found groups"""
    print("Testing found Facebook groups...")
    print("=" * 60)
    
    # Set up cookies
    os.environ['FACEBOOK_COOKIES'] = "c_user=100041694502927; xs=10%3ARNekcRU1BrqC6g%3A2%3A1752262070%3A-1%3A-1%3A%3AAcULfA9c9VIhI5PaJptFxPgYc2hfkunAA6SstNCZfA; datr=4CLQZvG8o8ZgHFphcrXHwulc; sb=S4oDZ-WL_4NuKpdWhnnVOtPD"
    
    test_params = {{
        "location": "Waterloo",
        "price_min": 500,
        "price_max": 1200,
        "term": "Fall",
        "stay_length": "8 months",
        "furnished": True,
        "gender": "Any",
        "lease_type": "Private"
    }}
    
    for i, group in enumerate(FOUND_GROUPS, 1):
        print(f"\\n[{{i}}/{{len(FOUND_GROUPS)}}] Testing group: {{group}}")
        print(f"URL: https://www.facebook.com/{{group}}")
        
        try:
            # Temporarily modify the sources to test just this group
            import app.scrapers.facebook as fb_module
            original_sources = fb_module.WATERLOO_HOUSING_SOURCES.copy()
            fb_module.WATERLOO_HOUSING_SOURCES = [group]
            
            results = await search_facebook(test_params)
            
            print(f"  Results: {{len(results)}} listings found")
            
            if results:
                for j, listing in enumerate(results[:3], 1):
                    print(f"    {{j}}. {{listing.get('title', 'No title')}}")
                    print(f"       Price: ${{listing.get('price', 'N/A')}}")
                    print(f"       Location: {{listing.get('location', 'N/A')}}")
                    print(f"       Score: {{listing.get('score', 0)}}")
            else:
                print("  No listings found")
                
        except Exception as e:
            print(f"  Error: {{e}}")
        
        # Restore original sources
        fb_module.WATERLOO_HOUSING_SOURCES = original_sources
        
        # Small delay between requests
        await asyncio.sleep(2)

async def main():
    """Main test function"""
    print("Found Groups Test Script")
    print("=" * 60)
    await test_found_groups()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open("test_found_groups.py", "w") as f:
        f.write(script_content)
    
    print("Created test_found_groups.py")

if __name__ == "__main__":
    asyncio.run(main()) 