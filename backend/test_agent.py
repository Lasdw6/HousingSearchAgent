#!/usr/bin/env python3
"""
Test script for the Housing Search Agent
Demonstrates the intelligent agent-based scraping capabilities
"""

import asyncio
import logging
from app.scrapers.agent import search_with_agent, HousingSearchAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_agent_search():
    """Test the agent with different search scenarios"""
    
    print("🏠 HOUSING SEARCH AGENT TEST")
    print("=" * 50)
    
    # Test scenarios
    test_scenarios = [
        {
            "name": "Basic Student Search",
            "params": {
                "gender": "Any",
                "price_min": 600,
                "price_max": 1200,
                "location": "Columbia",
                "term": "Fall",
                "stay_length": "8 months",
                "furnished": True,
                "lease_type": "Private"
            }
        },
        {
            "name": "Budget Search",
            "params": {
                "gender": "Any",
                "price_min": 400,
                "price_max": 800,
                "location": "Waterloo",
                "term": "Winter",
                "stay_length": "4 months",
                "furnished": False,
                "lease_type": "Shared"
            }
        },
        {
            "name": "Premium Search",
            "params": {
                "gender": "Any",
                "price_min": 1000,
                "price_max": 2000,
                "location": "University Avenue",
                "term": "Spring",
                "stay_length": "12 months",
                "furnished": True,
                "lease_type": "Private"
            }
        }
    ]
    
    # Test each scenario
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📋 Test {i}: {scenario['name']}")
        print("-" * 30)
        print(f"Parameters: {scenario['params']}")
        
        try:
            # Run agent search
            start_time = asyncio.get_event_loop().time()
            results = await search_with_agent(scenario['params'])
            end_time = asyncio.get_event_loop().time()
            
            print(f"⏱️  Search time: {end_time - start_time:.2f} seconds")
            print(f"📊 Found {len(results)} listings")
            
            # Show top 5 results
            print("\n🏆 Top 5 Results:")
            for j, listing in enumerate(results[:5], 1):
                print(f"  {j}. {listing['title'][:60]}...")
                print(f"     💰 ${listing.get('price', 'N/A')} | 📍 {listing.get('location', 'N/A')} | 🔗 {listing['source']}")
            
            if len(results) > 5:
                print(f"  ... and {len(results) - 5} more listings")
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print()

async def test_agent_learning():
    """Test the agent's learning capabilities"""
    
    print("\n🧠 AGENT LEARNING TEST")
    print("=" * 50)
    
    # Create agent instance
    agent = HousingSearchAgent()
    
    print("Initial agent state:")
    print(f"  State: {agent.state.value}")
    print(f"  Memory sources: {list(agent.memory.source_performance.keys())}")
    
    # Run multiple searches to see learning
    test_params = {
        "gender": "Any",
        "price_min": 600,
        "price_max": 1200,
        "location": "Columbia",
        "term": "Fall",
        "stay_length": "8 months",
        "furnished": True,
        "lease_type": "Private"
    }
    
    print("\nRunning multiple searches to observe learning...")
    
    for i in range(3):
        print(f"\n🔄 Search iteration {i + 1}")
        
        # Run search
        results = await agent.search_intelligently(test_params)
        
        print(f"  Results: {len(results)} listings")
        print(f"  Agent state: {agent.state.value}")
        
        # Show source performance
        print("  Source performance:")
        for source, performance in agent.memory.source_performance.items():
            print(f"    {source}: {performance:.2f}")
        
        # Wait between searches
        await asyncio.sleep(2)

async def test_agent_adaptation():
    """Test the agent's adaptation to different scenarios"""
    
    print("\n🔄 AGENT ADAPTATION TEST")
    print("=" * 50)
    
    agent = HousingSearchAgent()
    
    # Test different strategies
    strategies = [
        ("Broad Search", {"location": "Waterloo"}),
        ("Targeted Search", {"location": "Columbia", "price_min": 800, "price_max": 1200}),
        ("Fallback Search", {"location": "Unknown Area", "price_min": 200, "price_max": 400})
    ]
    
    for strategy_name, params in strategies:
        print(f"\n🎯 Testing: {strategy_name}")
        print(f"Parameters: {params}")
        
        # Add default parameters
        full_params = {
            "gender": "Any",
            "term": "Fall",
            "stay_length": "8 months",
            "furnished": False,
            "lease_type": "Any",
            **params
        }
        
        try:
            results = await agent.search_intelligently(full_params)
            print(f"  Results: {len(results)} listings")
            print(f"  Strategy used: {agent.state.value}")
            
        except Exception as e:
            print(f"  Error: {e}")

async def main():
    """Main test function"""
    print("🚀 Starting Housing Search Agent Tests")
    print("=" * 60)
    
    try:
        # Test basic search functionality
        await test_agent_search()
        
        # Test learning capabilities
        await test_agent_learning()
        
        # Test adaptation
        await test_agent_adaptation()
        
        print("\n✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 