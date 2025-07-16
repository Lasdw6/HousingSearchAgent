#!/usr/bin/env python3
"""
Test script to try specific Facebook groups that are known to exist
"""

import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from facebook_scraper import get_posts, set_cookies

def test_specific_groups():
    """Test specific Facebook groups that are known to exist"""
    
    # Real Facebook groups that exist (these are actual groups)
    test_groups = [
        "groups/waterloohousing",  # Waterloo Housing Group
        "groups/uwstudenthousing",  # UW Student Housing  
        "groups/waterloorentals",  # Waterloo Rentals
        "groups/uwstudentrentals",  # UW Student Rentals
        "groups/studenthousingcanada",  # Student Housing Canada
        "groups/ontariostudenthousing",  # Ontario Student Housing
    ]
    
    print("Testing specific Facebook groups...")
    print("=" * 50)
    
    for group in test_groups:
        print(f"\nTesting group: {group}")
        print(f"URL: https://www.facebook.com/{group}")
        
        try:
            # Try to get posts from the group
            posts = list(get_posts(
                group,
                pages=1,  # Just 1 page for testing
                timeout=15,
                options={
                    'allow_extra_requests': False,
                    'posts_per_page': 5,
                    'lang': 'en_US'
                }
            ))
            
            print(f"✓ Successfully accessed group")
            print(f"  Found {len(posts)} posts")
            
            # Show first post details if available
            if posts:
                first_post = posts[0]
                print(f"  First post:")
                print(f"    Text: {first_post.get('text', 'No text')[:100]}...")
                print(f"    Time: {first_post.get('time', 'No time')}")
                print(f"    Likes: {first_post.get('likes', 0)}")
                print(f"    Comments: {first_post.get('comments', 0)}")
            else:
                print("  No posts found")
                
        except Exception as e:
            print(f"✗ Error accessing group: {e}")
        
        print("-" * 30)

def test_with_cookies():
    """Test with session cookies if available"""
    cookies = os.getenv('FACEBOOK_COOKIES')
    if cookies:
        print("\n" + "=" * 50)
        print("TESTING WITH SESSION COOKIES")
        print("=" * 50)
        
        try:
            # Parse and set cookies
            cookie_dict = {}
            for cookie in cookies.split(';'):
                if '=' in cookie:
                    name, value = cookie.strip().split('=', 1)
                    cookie_dict[name] = value
            
            set_cookies(cookie_dict)
            print("✓ Session cookies set successfully")
            
            # Test a specific group with cookies
            test_group = "groups/waterloohousing"
            print(f"\nTesting {test_group} with session cookies...")
            
            posts = list(get_posts(
                test_group,
                pages=2,
                timeout=20,
                options={
                    'allow_extra_requests': True,
                    'posts_per_page': 10,
                    'lang': 'en_US'
                }
            ))
            
            print(f"✓ Found {len(posts)} posts with session cookies")
            
            # Show some post details
            for i, post in enumerate(posts[:3], 1):
                print(f"\nPost {i}:")
                print(f"  Text: {post.get('text', 'No text')[:150]}...")
                print(f"  Time: {post.get('time', 'No time')}")
                print(f"  Likes: {post.get('likes', 0)}")
                
        except Exception as e:
            print(f"✗ Error with session cookies: {e}")
    else:
        print("\nNo session cookies found. Set FACEBOOK_COOKIES environment variable to test with authentication.")

if __name__ == "__main__":
    print("FACEBOOK GROUP TESTING")
    print("=" * 50)
    
    # Test without cookies first
    test_specific_groups()
    
    # Test with cookies if available
    test_with_cookies()
    
    print("\n" + "=" * 50)
    print("TESTING COMPLETE")
    print("=" * 50) 