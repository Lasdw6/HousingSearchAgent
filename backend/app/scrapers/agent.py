import httpx
import asyncio
from typing import List, Dict, Optional, Any, Tuple
from selectolax.parser import HTMLParser
import re
from urllib.parse import urljoin, quote, urlparse
import logging
import random
import time
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class AgentState(Enum):
    EXPLORING = "exploring"
    LEARNING = "learning"
    OPTIMIZING = "optimizing"
    ADAPTING = "adapting"

class SearchStrategy(Enum):
    BROAD = "broad"
    TARGETED = "targeted"
    FALLBACK = "fallback"
    ADAPTIVE = "adaptive"

@dataclass
class SearchContext:
    """Context for the agent's search decisions"""
    source: str
    url: str
    strategy: SearchStrategy
    success_rate: float = 0.0
    last_success: Optional[float] = None
    failure_count: int = 0
    response_time: float = 0.0
    listing_count: int = 0

@dataclass
class AgentMemory:
    """Memory for the agent to learn from past searches"""
    successful_selectors: Dict[str, List[str]] = None
    failed_selectors: Dict[str, List[str]] = None
    source_performance: Dict[str, float] = None
    anti_bot_patterns: List[str] = None
    
    def __post_init__(self):
        if self.successful_selectors is None:
            self.successful_selectors = {}
        if self.failed_selectors is None:
            self.failed_selectors = {}
        if self.source_performance is None:
            self.source_performance = {}
        if self.anti_bot_patterns is None:
            self.anti_bot_patterns = []

class HousingSearchAgent:
    """Intelligent agent for searching housing listings across multiple sources"""
    
    def __init__(self, progress_callback=None):
        self.memory = AgentMemory()
        self.state = AgentState.EXPLORING
        self.contexts: Dict[str, SearchContext] = {}
        self.progress_callback = progress_callback
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0"
        ]
        
        # Define source configurations
        self.sources = {
            "kijiji": {
                "base_url": "https://www.kijiji.ca/b-for-rent/kitchener-waterloo/",
                "selectors": {
                    "listing_container": [
                        "div[data-testid='listing-card']",
                        "div[class*='listing-card']",
                        "div[class*='search-item']",
                        "div[class*='ad-item']",
                        "article[class*='listing']"
                    ],
                    "title": [
                        "h3[class*='title']",
                        "a[class*='title']",
                        "h3",
                        "h2"
                    ],
                    "price": [
                        "span[class*='price']",
                        "div[class*='price']",
                        "span[class*='amount']",
                        "p[class*='price']"
                    ],
                    "location": [
                        "span[class*='location']",
                        "div[class*='location']",
                        "span[class*='area']",
                        "p[class*='location']"
                    ],
                    "link": [
                        "a[href*='/v-apartments-condos/']",
                        "a[href*='/v-real-estate/']",
                        "a[class*='listing']",
                        "a"
                    ]
                },
                "search_params": {
                    "category": "k0c30349001l1700212",
                    "sort": "creationTimeDesc"
                }
            },
            "reddit": {
                "base_url": "https://www.reddit.com/r/uwaterloo/search.json",
                "api_params": {
                    "q": "housing OR rent OR apartment OR room",
                    "restrict_sr": "on",
                    "sort": "new",
                    "t": "month"
                }
            },
            "facebook": {
                "base_url": "https://www.facebook.com/marketplace/waterloo/search/",
                "selectors": {
                    "listing_container": [
                        "div[data-testid='marketplace_feed_item']",
                        "div[class*='marketplace-item']",
                        "div[class*='feed-item']"
                    ],
                    "title": [
                        "span[class*='title']",
                        "h3",
                        "div[class*='title']"
                    ],
                    "price": [
                        "span[class*='price']",
                        "div[class*='price']",
                        "span[class*='amount']"
                    ],
                    "location": [
                        "span[class*='location']",
                        "div[class*='location']"
                    ],
                    "link": [
                        "a[href*='/marketplace/item/']",
                        "a[class*='marketplace']"
                    ]
                }
            },
            "alternative_sources": {
                "base_url": "https://www.rentfaster.ca/on/waterloo-region",
                "selectors": {
                    "listing_container": [
                        "div[class*='listing']",
                        "div[class*='property']",
                        "div[class*='item']",
                        "article[class*='listing']"
                    ],
                    "title": [
                        "h3",
                        "h2",
                        "span[class*='title']",
                        "div[class*='title']"
                    ],
                    "price": [
                        "span[class*='price']",
                        "div[class*='price']",
                        "span[class*='amount']",
                        "p[class*='price']"
                    ],
                    "location": [
                        "span[class*='location']",
                        "div[class*='location']",
                        "span[class*='area']",
                        "p[class*='location']"
                    ],
                    "link": [
                        "a[href*='rent']",
                        "a[href*='property']",
                        "a[class*='listing']",
                        "a"
                    ]
                }
            }
        }
    
    async def search_intelligently(self, params: Dict) -> List[Dict]:
        """Main intelligent search method"""
        logger.info("=== HOUSING SEARCH AGENT START ===")
        logger.info(f"Search parameters: {params}")
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": "Initializing intelligent search agent...",
                "step": "init",
                "progress": 5
            })
        
        # Initialize search contexts
        self._initialize_contexts(params)
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": "Analyzing search strategy...",
                "step": "strategy",
                "progress": 10
            })
        
        # Determine search strategy
        strategy = self._determine_strategy()
        logger.info(f"Selected strategy: {strategy.value}")
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": f"Using {strategy.value} search strategy...",
                "step": "searching",
                "progress": 15
            })
        
        # Start with Google Playwright scraper (most effective)
        all_results = []
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": "Starting Google search with Playwright...",
                "step": "searching",
                "current_source": "Google Playwright",
                "progress": 20
            })
        
        try:
            from .google_playwright import search_google_playwright
            google_results = await search_google_playwright(params)
            
            if google_results:
                all_results.extend(google_results)
                logger.info(f"✓ Google Playwright: Found {len(google_results)} listings")
                
                if self.progress_callback:
                    await self.progress_callback({
                        "type": "progress",
                        "message": f"✓ Google Playwright: Found {len(google_results)} listings",
                        "step": "source_complete",
                        "current_source": "Google Playwright",
                        "progress": 60
                    })
            else:
                logger.warning("✗ Google Playwright: No listings found")
                
                if self.progress_callback:
                    await self.progress_callback({
                        "type": "progress",
                        "message": "✗ Google Playwright: No listings found",
                        "step": "source_complete",
                        "current_source": "Google Playwright",
                        "progress": 60
                    })
                    
        except Exception as e:
            logger.error(f"Error with Google Playwright: {e}")
            
            if self.progress_callback:
                await self.progress_callback({
                    "type": "progress",
                    "message": f"✗ Google Playwright: Error - {str(e)}",
                    "step": "source_error",
                    "current_source": "Google Playwright",
                    "progress": 60
                })
        
        # If we have enough results, skip other sources
        if len(all_results) >= 20:
            logger.info(f"Found sufficient results ({len(all_results)}), skipping other sources")
            
            if self.progress_callback:
                await self.progress_callback({
                    "type": "progress",
                    "message": f"Found sufficient results ({len(all_results)}), processing...",
                    "step": "processing",
                    "progress": 80
                })
        else:
            # Execute adaptive search for additional sources
            additional_results = await self._execute_adaptive_search(params, strategy)
            all_results.extend(additional_results)
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": f"Found {len(all_results)} total results, processing...",
                "step": "processing",
                "progress": 80
            })
        
        # Learn from results and update state
        self._learn_from_results(all_results)
        self._update_state(all_results)
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": f"Search completed! Found {len(all_results)} listings",
                "step": "complete",
                "progress": 95
            })
        
        logger.info(f"=== HOUSING SEARCH AGENT END - Found {len(all_results)} results ===")
        return all_results
    
    def _initialize_contexts(self, params: Dict):
        """Initialize search contexts for each source"""
        for source_name in self.sources.keys():
            self.contexts[source_name] = SearchContext(
                source=source_name,
                url=self.sources[source_name]["base_url"],
                strategy=SearchStrategy.BROAD,
                success_rate=self.memory.source_performance.get(source_name, 0.5)
            )
    
    def _determine_strategy(self) -> SearchStrategy:
        """Determine the best search strategy based on current state and memory"""
        if self.state == AgentState.EXPLORING:
            return SearchStrategy.BROAD
        elif self.state == AgentState.LEARNING:
            return SearchStrategy.ADAPTIVE
        elif self.state == AgentState.OPTIMIZING:
            return SearchStrategy.TARGETED
        else:  # ADAPTING
            return SearchStrategy.FALLBACK
    
    async def _execute_adaptive_search(self, params: Dict, strategy: SearchStrategy) -> List[Dict]:
        """Execute search with adaptive approach"""
        all_results = []
        
        # Prioritize sources based on performance
        source_priority = self._get_source_priority()
        
        for i, source_name in enumerate(source_priority):
            try:
                context = self.contexts[source_name]
                logger.info(f"Searching {source_name} with strategy {strategy.value}")
                
                if self.progress_callback:
                    await self.progress_callback({
                        "type": "progress",
                        "message": f"Searching {source_name.title()}...",
                        "step": "searching",
                        "current_source": source_name.title(),
                        "progress": 15 + (i * 15)  # 15% to 75% for searching
                    })
                
                # Adapt strategy based on source performance
                adapted_strategy = self._adapt_strategy_for_source(strategy, context)
                
                # Execute search for this source
                source_results = await self._search_source(source_name, params, adapted_strategy)
                
                if source_results:
                    all_results.extend(source_results)
                    context.success_rate = min(1.0, context.success_rate + 0.1)
                    context.last_success = time.time()
                    context.listing_count = len(source_results)
                    logger.info(f"✓ {source_name}: Found {len(source_results)} listings")
                    
                    if self.progress_callback:
                        await self.progress_callback({
                            "type": "progress",
                            "message": f"✓ {source_name.title()}: Found {len(source_results)} listings",
                            "step": "source_complete",
                            "current_source": source_name.title(),
                            "progress": 20 + (i * 15)
                        })
                else:
                    context.failure_count += 1
                    context.success_rate = max(0.0, context.success_rate - 0.1)
                    logger.warning(f"✗ {source_name}: No listings found")
                    
                    if self.progress_callback:
                        await self.progress_callback({
                            "type": "progress",
                            "message": f"✗ {source_name.title()}: No listings found",
                            "step": "source_complete",
                            "current_source": source_name.title(),
                            "progress": 20 + (i * 15)
                        })
                
                # Add delay to be respectful
                await asyncio.sleep(random.uniform(1, 3))
                
            except Exception as e:
                logger.error(f"Error searching {source_name}: {e}")
                self.contexts[source_name].failure_count += 1
                
                if self.progress_callback:
                    await self.progress_callback({
                        "type": "progress",
                        "message": f"✗ {source_name.title()}: Error - {str(e)}",
                        "step": "source_error",
                        "current_source": source_name.title(),
                        "progress": 20 + (i * 15)
                    })
        
        if self.progress_callback:
            await self.progress_callback({
                "type": "progress",
                "message": f"Processing {len(all_results)} total listings...",
                "step": "processing",
                "progress": 80
            })
        
        return all_results
    
    def _get_source_priority(self) -> List[str]:
        """Get prioritized list of sources based on performance"""
        # Sort sources by success rate and recent performance
        source_scores = []
        for source_name, context in self.contexts.items():
            score = context.success_rate
            if context.last_success:
                # Boost recent successes
                time_since_success = time.time() - context.last_success
                if time_since_success < 3600:  # Within last hour
                    score += 0.2
            
            source_scores.append((source_name, score))
        
        # Sort by score (highest first)
        source_scores.sort(key=lambda x: x[1], reverse=True)
        return [source for source, score in source_scores]
    
    def _adapt_strategy_for_source(self, base_strategy: SearchStrategy, context: SearchContext) -> SearchStrategy:
        """Adapt strategy based on source performance"""
        if context.success_rate < 0.3:
            return SearchStrategy.FALLBACK
        elif context.success_rate > 0.7:
            return SearchStrategy.TARGETED
        else:
            return base_strategy
    
    async def _search_source(self, source_name: str, params: Dict, strategy: SearchStrategy) -> List[Dict]:
        """Search a specific source with intelligent adaptation and fallback to individual scrapers"""
        source_config = self.sources[source_name]
        context = self.contexts[source_name]
        
        # Try agent-based search first
        try:
            if source_name == "reddit":
                results = await self._search_reddit_api(params, strategy)
            elif source_name == "alternative_sources":
                # Use the alternative sources scraper directly
                from .alternative_sources import search_alternative_sources
                results = await search_alternative_sources(params)
            else:
                results = await self._search_web_page(source_name, source_config, params, strategy)
            
            if results:
                return results
                
        except Exception as e:
            logger.warning(f"Agent search failed for {source_name}: {e}")
        
        # Fallback to individual scrapers
        try:
            if source_name == "kijiji":
                from .kijiji import search_kijiji
                results = await search_kijiji(params)
            elif source_name == "facebook":
                from .facebook import search_facebook
                results = await search_facebook(params)
            elif source_name == "reddit":
                from .reddit import search_reddit
                results = await search_reddit(params)
            elif source_name == "google":
                from .google import search_google
                results = await search_google(params)
            elif source_name == "uw_offcampus":
                from .uw_offcampus import search_uw_offcampus
                results = await search_uw_offcampus(params)
            elif source_name == "craigslist":
                from .craigslist import search_craigslist
                results = await search_craigslist(params)
            elif source_name == "rentals_ca":
                from .rentals_ca import search_rentals_ca
                results = await search_rentals_ca(params)
            else:
                results = []
            
            if results:
                logger.info(f"Fallback scraper for {source_name} found {len(results)} listings")
                return results
                
        except Exception as e:
            logger.warning(f"Fallback scraper failed for {source_name}: {e}")
        
        # No results found
        return []
    
    async def _search_web_page(self, source_name: str, config: Dict, params: Dict, strategy: SearchStrategy) -> List[Dict]:
        """Search web page with intelligent selector adaptation"""
        # Build search URL
        search_url = self._build_search_url(config, params, strategy)
        
        # Try different approaches based on strategy
        approaches = self._get_search_approaches(strategy)
        
        for approach in approaches:
            try:
                results = await self._try_approach(source_name, search_url, config, approach)
                if results:
                    logger.info(f"Success with approach {approach} for {source_name}")
                    return results
            except Exception as e:
                logger.warning(f"Approach {approach} failed for {source_name}: {e}")
                continue
        
        return []
    
    def _build_search_url(self, config: Dict, params: Dict, strategy: SearchStrategy) -> str:
        """Build search URL based on strategy"""
        base_url = config["base_url"]
        
        if strategy == SearchStrategy.BROAD:
            # Use broad search terms
            search_terms = ["waterloo", "student", "housing", "rent"]
        elif strategy == SearchStrategy.TARGETED:
            # Use specific search terms
            search_terms = []
            if params.get("location"):
                search_terms.append(params["location"])
            if params.get("term"):
                search_terms.append(params["term"])
            search_terms.extend(["student", "housing"])
        else:  # FALLBACK
            # Use minimal search terms
            search_terms = ["waterloo", "rent"]
        
        query = " ".join(search_terms)
        return f"{base_url}?query={quote(query)}"
    
    def _get_search_approaches(self, strategy: SearchStrategy) -> List[str]:
        """Get list of approaches to try based on strategy"""
        if strategy == SearchStrategy.BROAD:
            return ["standard", "alternative_selectors", "fallback_selectors"]
        elif strategy == SearchStrategy.TARGETED:
            return ["standard", "precise_selectors"]
        else:  # FALLBACK
            return ["fallback_selectors", "minimal_selectors"]
    
    async def _try_approach(self, source_name: str, url: str, config: Dict, approach: str) -> List[Dict]:
        """Try a specific search approach"""
        headers = self._get_headers(approach)
        
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"HTTP {response.status_code}")
            
            # Parse with different selector strategies
            if approach == "standard":
                return self._parse_with_selectors(response.text, config["selectors"], source_name)
            elif approach == "alternative_selectors":
                return self._parse_with_alternative_selectors(response.text, source_name)
            elif approach == "fallback_selectors":
                return self._parse_with_fallback_selectors(response.text, source_name)
            elif approach == "minimal_selectors":
                return self._parse_with_minimal_selectors(response.text, source_name)
            else:
                return []
    
    def _get_headers(self, approach: str) -> Dict[str, str]:
        """Get headers based on approach"""
        user_agent = random.choice(self.user_agents)
        
        headers = {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        if approach == "standard":
            headers["Sec-Fetch-Dest"] = "document"
            headers["Sec-Fetch-Mode"] = "navigate"
            headers["Sec-Fetch-Site"] = "none"
        
        return headers
    
    def _parse_with_selectors(self, html: str, selectors: Dict, source_name: str) -> List[Dict]:
        """Parse HTML using configured selectors"""
        parser = HTMLParser(html)
        listings = []
        
        # Try each selector for listing containers
        for container_selector in selectors["listing_container"]:
            elements = parser.css(container_selector)
            if elements:
                for element in elements[:20]:  # Limit results
                    listing = self._extract_listing_data(element, selectors, source_name)
                    if listing:
                        listings.append(listing)
                break
        
        return listings
    
    def _parse_with_alternative_selectors(self, html: str, source_name: str) -> List[Dict]:
        """Parse with alternative selectors when standard ones fail"""
        parser = HTMLParser(html)
        listings = []
        
        # Try generic selectors
        generic_selectors = {
            "listing_container": ["div", "article", "li"],
            "title": ["h1", "h2", "h3", "h4", "a"],
            "price": ["span", "div", "p"],
            "location": ["span", "div", "p"],
            "link": ["a"]
        }
        
        return self._parse_with_selectors(html, generic_selectors, source_name)
    
    def _parse_with_fallback_selectors(self, html: str, source_name: str) -> List[Dict]:
        """Parse with very basic fallback selectors"""
        parser = HTMLParser(html)
        listings = []
        
        # Look for any links that might be listings
        links = parser.css("a[href*='listing']") or parser.css("a[href*='property']") or parser.css("a[href*='rent']")
        
        for link in links[:10]:
            title = link.text().strip()
            if title and len(title) > 10:
                listings.append({
                    "title": title,
                    "price": None,
                    "location": "Waterloo",
                    "source": source_name.title(),
                    "url": urljoin("https://example.com", link.attributes.get("href", ""))
                })
        
        return listings
    
    def _parse_with_minimal_selectors(self, html: str, source_name: str) -> List[Dict]:
        """Parse with minimal selectors for basic extraction"""
        # This is a very basic fallback
        return []
    
    def _extract_listing_data(self, element, selectors: Dict, source_name: str) -> Optional[Dict]:
        """Extract listing data from an element"""
        try:
            # Extract title
            title = self._extract_text(element, selectors["title"])
            if not title:
                return None
            
            # Extract other fields
            price = self._extract_price(self._extract_text(element, selectors["price"]))
            location = self._extract_text(element, selectors["location"]) or "Waterloo"
            url = self._extract_url(element, selectors["link"])
            
            return {
                "title": title,
                "price": price,
                "location": location,
                "source": source_name.title(),
                "url": url
            }
        except Exception as e:
            logger.debug(f"Error extracting listing data: {e}")
            return None
    
    def _extract_text(self, element, selectors: List[str]) -> Optional[str]:
        """Extract text using multiple selectors"""
        for selector in selectors:
            elem = element.css_first(selector)
            if elem:
                return elem.text().strip()
        return None
    
    def _extract_price(self, price_text: str) -> Optional[int]:
        """Extract price from text"""
        if not price_text:
            return None
        
        # Remove common text and symbols
        price_text = re.sub(r'[^\d]', '', price_text)
        
        try:
            price = int(price_text)
            if 400 <= price <= 2000:  # Reasonable range for student housing
                return price
        except ValueError:
            pass
        
        return None
    
    def _extract_url(self, element, selectors: List[str]) -> str:
        """Extract URL from element"""
        for selector in selectors:
            elem = element.css_first(selector)
            if elem:
                href = elem.attributes.get("href", "")
                if href:
                    return urljoin("https://example.com", href)
        return "https://example.com"
    
    async def _search_reddit_api(self, params: Dict, strategy: SearchStrategy) -> List[Dict]:
        """Search Reddit API"""
        # This would implement Reddit API search
        # For now, return empty list if nothing is found
        return []
    
    def _learn_from_results(self, results: List[Dict]):
        """Learn from search results and update memory"""
        # Update source performance
        for result in results:
            source = result["source"].lower()
            if source in self.memory.source_performance:
                self.memory.source_performance[source] += 0.01
            else:
                self.memory.source_performance[source] = 0.5
    
    def _update_state(self, results: List[Dict]):
        """Update agent state based on results"""
        if len(results) > 20:
            self.state = AgentState.OPTIMIZING
        elif len(results) > 10:
            self.state = AgentState.LEARNING
        elif len(results) > 0:
            self.state = AgentState.ADAPTING
        else:
            self.state = AgentState.EXPLORING

# Global agent instance
housing_agent = HousingSearchAgent()

async def search_with_agent(params: Dict, progress_callback=None) -> List[Dict]:
    """Main function to search using the intelligent agent"""
    if progress_callback:
        agent = HousingSearchAgent(progress_callback=progress_callback)
        return await agent.search_intelligently(params)
    else:
        return await housing_agent.search_intelligently(params) 