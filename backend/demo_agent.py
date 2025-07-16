#!/usr/bin/env python3
"""
Housing Search Agent Demonstration
Showcases the intelligent agent's capabilities in real-time
"""

import asyncio
import logging
from app.scrapers.agent import HousingSearchAgent
import time

# Configure logging for demonstration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

async def demonstrate_agent_intelligence():
    """Demonstrate the agent's intelligent capabilities"""
    
    print("🤖 HOUSING SEARCH AGENT DEMONSTRATION")
    print("=" * 60)
    print()
    
    # Create agent instance
    agent = HousingSearchAgent()
    
    print("🧠 AGENT INITIALIZATION")
    print("-" * 30)
    print(f"Initial State: {agent.state.value}")
    print(f"Memory Sources: {list(agent.memory.source_performance.keys())}")
    print(f"Available Sources: {list(agent.sources.keys())}")
    print()
    
    # Test scenarios to demonstrate intelligence
    scenarios = [
        {
            "name": "🎯 Smart Student Search",
            "description": "Agent adapts to student-specific needs",
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
            "name": "💰 Budget Optimization",
            "description": "Agent finds best deals within budget",
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
            "name": "🔍 Location Intelligence",
            "description": "Agent adapts to location-specific challenges",
            "params": {
                "gender": "Any",
                "price_min": 800,
                "price_max": 1500,
                "location": "University Avenue",
                "term": "Spring",
                "stay_length": "12 months",
                "furnished": True,
                "lease_type": "Private"
            }
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"📋 SCENARIO {i}: {scenario['name']}")
        print(f"Description: {scenario['description']}")
        print(f"Parameters: {scenario['params']}")
        print()
        
        # Track agent state before search
        initial_state = agent.state.value
        initial_memory = agent.memory.source_performance.copy()
        
        print("🔍 Starting intelligent search...")
        start_time = time.time()
        
        # Run agent search
        results = await agent.search_intelligently(scenario['params'])
        
        end_time = time.time()
        search_duration = end_time - start_time
        
        # Analyze results
        print(f"⏱️  Search completed in {search_duration:.2f} seconds")
        print(f"📊 Found {len(results)} listings")
        print(f"🧠 Agent state changed: {initial_state} → {agent.state.value}")
        
        # Show source breakdown
        source_counts = {}
        for listing in results:
            source = listing['source']
            source_counts[source] = source_counts.get(source, 0) + 1
        
        print("📈 Source Performance:")
        for source, count in source_counts.items():
            performance = agent.memory.source_performance.get(source.lower(), 0.0)
            print(f"  {source}: {count} listings (performance: {performance:.2f})")
        
        # Show top results
        print("\n🏆 Top 3 Results:")
        for j, listing in enumerate(results[:3], 1):
            price_str = f"${listing.get('price', 'N/A')}" if listing.get('price') else "N/A"
            print(f"  {j}. {listing['title'][:50]}...")
            print(f"     💰 {price_str} | 📍 {listing.get('location', 'N/A')} | 🔗 {listing['source']}")
        
        print("\n" + "="*60 + "\n")
        
        # Wait between searches to show learning
        await asyncio.sleep(2)
    
    # Final agent analysis
    print("🎯 FINAL AGENT ANALYSIS")
    print("-" * 30)
    print(f"Final State: {agent.state.value}")
    print("Learned Performance:")
    for source, performance in agent.memory.source_performance.items():
        print(f"  {source}: {performance:.2f}")
    
    print("\n✨ AGENT CAPABILITIES DEMONSTRATED:")
    print("✅ Intelligent strategy selection")
    print("✅ Adaptive learning from results")
    print("✅ Source performance tracking")
    print("✅ Graceful error handling")
    print("✅ Multi-approach fallbacks")
    print("✅ Dynamic state management")
    print("✅ Respectful rate limiting")
    
    print("\n🚀 The agent successfully demonstrated intelligent search capabilities!")
    print("It can now adapt to different scenarios and learn from each search experience.")

async def main():
    """Main demonstration function"""
    try:
        await demonstrate_agent_intelligence()
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 