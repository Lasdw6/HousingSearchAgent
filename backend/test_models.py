#!/usr/bin/env python3
"""
Test script to verify the updated models work correctly
"""

from app.models import Listing, RelatedLink

def test_models():
    """Test the updated models"""
    print("Testing updated models...")
    
    # Test RelatedLink model
    related_link = RelatedLink(
        url="https://example.com",
        text="Example Link",
        reason="This is a test link"
    )
    print(f"✅ RelatedLink created: {related_link.url}")
    
    # Test Listing model with related links
    listing = Listing(
        title="Test Listing",
        price=800,
        location="Waterloo",
        source="Test Source",
        url="https://example.com/listing",
        description="Test description",
        relevance_score=85.5,
        related_links=[related_link]
    )
    print(f"✅ Listing created: {listing.title}")
    print(f"✅ Related links: {len(listing.related_links)}")
    
    # Test Listing model without related links
    listing2 = Listing(
        title="Test Listing 2",
        price=900,
        location="Kitchener",
        source="Test Source 2",
        url="https://example.com/listing2"
    )
    print(f"✅ Listing without related links created: {listing2.title}")
    
    print("\n🎉 All model tests passed!")
    return True

if __name__ == "__main__":
    test_models()

