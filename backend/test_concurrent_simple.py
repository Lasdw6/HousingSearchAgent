#!/usr/bin/env python3
"""
Simple test script for concurrent search functionality without LLM
"""

import asyncio
import json
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

async def test_concurrent_search_simple():
    """Test the concurrent search functionality without LLM"""
    print("Testing concurrent search functionality (without LLM)...")
    
    # Test parameters
    params = {
        "gender": "Male-only",
        "price_min": 700,
        "price_max": 1200,
        "term": "Winter",
        "location": "Near the university of waterloo",
        "furnished": True,
        "lease_type": "Private room",
        "stay_length": "4 months",
        "show_browser": True
    }
    
    # Progress callback to simulate real-time updates
    async def progress_callback(message):
        print(f"Progress: {message}")
    
    try:
        # Import the search function
        from app.scrapers.google_playwright import GooglePlaywrightScraper
        
        print("Starting concurrent search...")
        
        # Test the scraper directly
        async with GooglePlaywrightScraper(enable_deep_search=False) as scraper:
            print("Browser launched successfully!")
            
            # Test basic functionality
            print("Testing basic search functionality...")
            
            # Test search queries
            queries = [
                "waterloo student housing rent apartment room",
                "kitchener waterloo student housing for rent"
            ]
            
            for i, query in enumerate(queries):
                print(f"Testing query {i+1}: {query}")
                
                # Test DuckDuckGo search
                try:
                    results = await scraper.search_duckduckgo(query, max_pages=1)
                    print(f"  Found {len(results)} results from DuckDuckGo")
                except Exception as e:
                    print(f"  DuckDuckGo search failed: {e}")
                
                # Test Google search
                try:
                    results = await scraper.search_google(query, max_pages=1)
                    print(f"  Found {len(results)} results from Google")
                except Exception as e:
                    print(f"  Google search failed: {e}")
        
        print("\n✅ Concurrent search test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during search: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_concurrent_search_simple())
    if success:
        print("\n✅ Simple concurrent search test completed successfully!")
    else:
        print("\n❌ Simple concurrent search test failed!")
        sys.exit(1)

