# Housing Search Scrapers

This directory contains web scrapers for collecting housing listings from various sources for University of Waterloo students. The system now features an **intelligent agent-based approach** that can adapt and learn from search patterns.

## 🧠 Intelligent Agent System

### Agent-Based Scraper (`agent.py`)

The new **HousingSearchAgent** is an intelligent system that:

- **Adapts to website changes** automatically
- **Learns from search results** to improve performance
- **Prioritizes sources** based on success rates
- **Falls back gracefully** when scraping fails
- **Uses multiple strategies** for different scenarios

#### Agent States

1. **EXPLORING**: Initial state, uses broad search strategies
2. **LEARNING**: Adapts based on initial results
3. **OPTIMIZING**: Uses targeted strategies for best sources
4. **ADAPTING**: Adjusts when sources fail

#### Search Strategies

- **BROAD**: Wide search terms for maximum coverage
- **TARGETED**: Specific terms for precision
- **FALLBACK**: Minimal terms when others fail
- **ADAPTIVE**: Dynamic strategy selection

#### Key Features

- **Memory System**: Remembers successful selectors and source performance
- **Intelligent Fallbacks**: Uses existing scrapers when agent fails
- **Rate Limiting**: Respectful delays between requests
- **Error Recovery**: Multiple approaches per source
- **Performance Tracking**: Learns which sources work best

## Available Scrapers

### 1. Kijiji Scraper (`kijiji.py`)

- **Source**: Kijiji.ca - Popular Canadian classifieds website
- **URL**: https://www.kijiji.ca/b-for-rent/kitchener-waterloo/
- **Features**:
  - Real-time web scraping with fallback to mock data
  - Multiple CSS selector strategies for robustness
  - Price extraction and filtering
  - Location-based filtering

### 2. Reddit Scraper (`reddit.py`)

- **Source**: Reddit r/uwaterloo subreddit
- **URL**: https://www.reddit.com/r/uwaterloo/
- **Features**:
  - Uses Reddit JSON API
  - Filters for housing-related posts
  - Price extraction from post titles and text
  - Location detection from post content

### 3. Facebook Marketplace Scraper (`facebook.py`)

- **Source**: Facebook Marketplace
- **Note**: Uses mock data due to Facebook's strict anti-scraping measures
- **Features**:
  - Realistic mock data generation
  - Parameter-based customization
  - Comprehensive filtering options

### 4. Rentals.ca Scraper (`rentals_ca.py`)

- **Source**: Rentals.ca - Canadian rental listings
- **URL**: https://www.rentals.ca/on/waterloo-region/
- **Features**:
  - Real-time web scraping with fallback to mock data
  - Multiple selector strategies
  - Price and location extraction

### 5. UW Off-Campus Housing Scraper (`uw_offcampus.py`)

- **Source**: University of Waterloo Off-Campus Housing
- **URL**: https://offcampushousing.uwaterloo.ca/
- **Features**:
  - UW-specific housing listings
  - Highest priority scoring in search results
  - Student-focused filtering

### 6. Google Search Scraper (`google.py`)

- **Source**: Google News Search
- **URL**: https://www.google.com/search?tbm=nws
- **Features**:
  - Searches Google News for housing-related articles and listings
  - Filters results to only housing-related content
  - Extracts actual URLs from Google's redirect links
  - Price and location extraction from search snippets
  - Good for finding listings from diverse sources

### 7. Craigslist Scraper (`craigslist.py`)

- **Source**: Craigslist Kitchener-Waterloo
- **URL**: https://kitchener.craigslist.org/search/apa
- **Features**:
  - Local classifieds listings
  - Price and location extraction
  - Multiple selector strategies

## How to Use

### Using the Intelligent Agent (Recommended)

```python
from app.scrapers.agent import search_with_agent

# Sample parameters
params = {
    "location": "Columbia",
    "price_min": 500,
    "price_max": 1200,
    "term": "Fall",
    "stay_length": "8 months",
    "furnished": True,
    "gender": "Any",
    "lease_type": "Private"
}

# The agent will intelligently search all sources
results = await search_with_agent(params)
```

### Running Individual Scrapers

```python
from app.scrapers import search_kijiji, search_reddit, search_facebook, search_google

# Sample parameters
params = {
    "location": "Columbia",
    "price_min": 500,
    "price_max": 1200,
    "term": "Fall",
    "stay_length": "8 months",
    "furnished": True,
    "gender": "Any",
    "lease_type": "Private"
}

# Run individual scrapers
kijiji_results = await search_kijiji(params)
reddit_results = await search_reddit(params)
facebook_results = await search_facebook(params)
google_results = await search_google(params)
```

### Testing the Agent

Run the comprehensive test script to see the agent in action:

```bash
cd backend
python test_agent.py
```

This will demonstrate:

- Multiple search scenarios
- Learning capabilities
- Adaptation to different strategies
- Performance tracking

## Agent Features

### Intelligent Decision Making

The agent makes decisions based on:

1. **Historical Performance**: Remembers which sources work best
2. **Current State**: Adapts strategy based on recent results
3. **User Parameters**: Tailors search approach to specific needs
4. **Error Patterns**: Learns from failures to avoid them

### Adaptive Search Strategies

- **Broad Strategy**: Uses general terms like "waterloo student housing"
- **Targeted Strategy**: Uses specific terms like "Columbia Street furnished"
- **Fallback Strategy**: Uses minimal terms when others fail
- **Adaptive Strategy**: Dynamically switches between approaches

### Memory and Learning

The agent maintains:

- **Source Performance**: Success rates for each source
- **Successful Selectors**: CSS selectors that work for each site
- **Failed Patterns**: Anti-bot patterns to avoid
- **Response Times**: Performance metrics for optimization

### Graceful Degradation

When the agent's intelligent scraping fails, it:

1. Tries alternative selectors
2. Falls back to existing scrapers
3. Uses minimal extraction methods
4. Generates realistic mock data as last resort

## Scraper Features

### Common Features Across All Scrapers

1. **Error Handling**: All scrapers have comprehensive error handling with fallback to mock data
2. **Timeout Protection**: 30-second timeout per scraper to prevent hanging
3. **Logging**: Detailed logging for debugging and monitoring
4. **Filtering**: All scrapers apply user filters (price, location, gender, etc.)
5. **Mock Data**: Realistic fallback data when scraping fails

### Data Structure

Each scraper returns a list of dictionaries with the following structure:

```python
{
    "title": "Listing title",
    "price": 800,  # Price in CAD, or None if not available
    "location": "Columbia Street",
    "source": "Kijiji",  # Source name
    "url": "https://example.com/listing"
}
```

### Filtering Logic

All scrapers implement the same filtering logic:

- **Price Range**: Filters by minimum and maximum price
- **Location**: Matches location keywords in listing title/location
- **Gender**: Filters by gender-specific requirements
- **Term**: Matches academic term requirements
- **Stay Length**: Matches lease duration requirements

## Configuration

### Headers and User Agents

All scrapers use realistic browser headers to avoid being blocked:

```python
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}
```

### Timeouts

- Individual scraper timeout: 30 seconds
- Overall search timeout: 90 seconds
- Graceful degradation when timeouts occur

## Dependencies

Required Python packages:

```
httpx==0.25.2          # HTTP client for async requests
selectolax==0.3.12     # Fast HTML parsing
beautifulsoup4==4.12.2 # HTML parsing (backup)
```

## Troubleshooting

### Common Issues

1. **No listings found**: Check if the website structure has changed
2. **Timeout errors**: Increase timeout values or check network connectivity
3. **Blocked requests**: Update User-Agent headers or add delays between requests

### Debugging

Enable detailed logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Mock Data Fallback

When scraping fails, all scrapers fall back to realistic mock data that:

- Matches user search parameters
- Provides varied listings across different sources
- Maintains realistic pricing and locations
- Includes proper URLs and titles

## Future Improvements

1. **Rate Limiting**: Add delays between requests to be more respectful
2. **Proxy Support**: Add proxy rotation to avoid IP blocking
3. **Caching**: Implement result caching to reduce repeated requests
4. **More Sources**: Add additional housing websites
5. **Image Scraping**: Extract and display listing images
6. **Contact Information**: Extract contact details when available
7. **Machine Learning**: Use ML to predict which sources will work best
8. **Dynamic Selector Learning**: Automatically discover new selectors
9. **Anti-Bot Detection**: Better detection and avoidance of blocking
10. **Performance Optimization**: Parallel processing and smart queuing
