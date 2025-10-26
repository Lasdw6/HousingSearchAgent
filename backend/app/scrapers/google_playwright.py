import asyncio
import re
import logging
import os
from typing import List, Dict, Optional, Set, Tuple
from playwright.async_api import async_playwright, Browser, Page
from urllib.parse import urlparse, unquote
import random
import time
import json

logger = logging.getLogger(__name__)

async def generate_llm_search_queries(params: Dict) -> List[str]:
    """
    Generate 5 optimized search queries using LLM based on user parameters
    """
    try:
        # Import OpenAI here to avoid import errors if not available
        from openai import AsyncOpenAI
        
        # Initialize OpenAI client
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Extract key parameters
        location = params.get('location', 'Waterloo')
        price_min = params.get('price_min', 400)
        price_max = params.get('price_max', 1500)
        term = params.get('term', '')
        furnished = params.get('furnished')
        lease_type = params.get('lease_type', '')
        gender = params.get('gender', 'Any')
        
        # Build context for LLM
        context = f"""
        Generate 5 optimized search queries for finding student housing in {location}.
        
        User Requirements:
        - Location: {location}
        - Price Range: ${price_min}-${price_max}
        - Term: {term if term else 'Any'}
        - Furnished: {'Yes' if furnished else 'No' if furnished is False else 'Any'}
        - Lease Type: {lease_type if lease_type else 'Any'}
        - Gender: {gender}
        
        Return ONLY a JSON array of exactly 5 search query strings. No other text, no explanations, just the JSON array.
        
        Example format:
        ["query 1", "query 2", "query 3", "query 4", "query 5"]
        """
        
        print("Generating optimized search queries using LLM...")
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", 
                    "content": "You are an expert at generating search queries for student housing. You MUST return only a valid JSON array of exactly 5 strings. No other text, no explanations, no markdown formatting."
                },
                {
                    "role": "user", 
                    "content": context
                }
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Parse the response
        content = response.choices[0].message.content.strip()
        print(f"LLM Response: {content}")
        
        # Check if response is empty
        if not content:
            print("LLM returned empty response")
            raise ValueError("LLM returned empty response")
        
        # Try to parse as JSON
        try:
            queries = json.loads(content)
            if isinstance(queries, list) and len(queries) == 5:
                print(f"Generated {len(queries)} LLM-optimized queries:")
                for i, query in enumerate(queries, 1):
                    print(f"  {i}. {query}")
                return queries
            else:
                print(f"Invalid response format: expected list of 5 queries, got {type(queries)} with {len(queries) if isinstance(queries, list) else 'N/A'} items")
                raise ValueError("Invalid response format")
        except (json.JSONDecodeError, ValueError) as e:
            print(f"LLM response parsing failed: {e}")
            print(f"Raw response: '{content}'")
            print(f"Response length: {len(content)}")
            raise e
            
    except ImportError:
        print("OpenAI not available - LLM is required for intelligent search")
        raise Exception("OpenAI API key is required for intelligent search")
    except Exception as e:
        print(f"LLM query generation failed: {e}")
        raise Exception(f"LLM query generation failed: {e}")

async def evaluate_page_with_llm(url: str, page_content: str, params: Dict) -> Dict:
    """
    Use LLM to intelligently evaluate a page for housing relevance
    Returns: {is_relevant: bool, relevance_score: float, reasoning: str, extracted_listings: List[Dict]}
    """
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Extract key parameters for context
        location = params.get('location', 'Waterloo')
        price_min = params.get('price_min', 400)
        price_max = params.get('price_max', 1500)
        term = params.get('term', '')
        furnished = params.get('furnished')
        lease_type = params.get('lease_type', '')
        gender = params.get('gender', 'Any')
        
        # Truncate content if too long (keep first 4000 chars for context)
        content_preview = page_content[:4000] if len(page_content) > 4000 else page_content
        
        context = f"""
        You are an intelligent housing search agent. Analyze this webpage for student housing listings.
        
        User Requirements:
        - Location: {location}
        - Price Range: ${price_min}-${price_max}
        - Term: {term if term else 'Any'}
        - Furnished: {'Yes' if furnished else 'No' if furnished is False else 'Any'}
        - Lease Type: {lease_type if lease_type else 'Any'}
        - Gender: {gender}
        
        Webpage URL: {url}
        Webpage Content: {content_preview}
        
        Analyze this page and determine:
        1. Is this page relevant for student housing? (true/false)
        2. What is the relevance score? (0-100)
        3. What is your reasoning?
        4. Extract any housing listings found (title, price, location, description, url)
        
        Return your analysis as JSON:
        {{
            "is_relevant": boolean,
            "relevance_score": number (0-100),
            "reasoning": "string explaining your analysis",
            "extracted_listings": [
                {{
                    "title": "string",
                    "price": number or null,
                    "location": "string",
                    "description": "string",
                    "url": "string"
                }}
            ]
        }}
        """
        
        print(f"Using LLM to analyze page: {url}")
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at analyzing web pages for student housing. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            max_tokens=1000,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            analysis = json.loads(content)
            print(f"LLM Analysis: {analysis.get('reasoning', 'No reasoning provided')}")
            return analysis
        except json.JSONDecodeError as e:
            print(f"LLM response parsing failed: {e}")
            return {
                "is_relevant": False,
                "relevance_score": 0,
                "reasoning": f"Failed to parse LLM response: {e}",
                "extracted_listings": []
            }
            
    except Exception as e:
        print(f"LLM page evaluation failed: {e}")
        return {
            "is_relevant": False,
            "relevance_score": 0,
            "reasoning": f"LLM evaluation failed: {e}",
            "extracted_listings": []
        }

async def evaluate_link_with_llm(link_url: str, link_text: str, page_context: str, params: Dict) -> Dict:
    """
    Use LLM to intelligently evaluate if a link is worth following
    Returns: {is_relevant: bool, relevance_score: float, reasoning: str}
    """
    try:
        from openai import AsyncOpenAI
        
        client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Extract key parameters
        location = params.get('location', 'Waterloo')
        price_min = params.get('price_min', 400)
        price_max = params.get('price_max', 1500)
        term = params.get('term', '')
        furnished = params.get('furnished')
        lease_type = params.get('lease_type', '')
        gender = params.get('gender', 'Any')
        
        context = f"""
        You are an intelligent housing search agent. Evaluate if this link is worth following for student housing.
        
        User Requirements:
        - Location: {location}
        - Price Range: ${price_min}-${price_max}
        - Term: {term if term else 'Any'}
        - Furnished: {'Yes' if furnished else 'No' if furnished is False else 'Any'}
        - Lease Type: {lease_type if lease_type else 'Any'}
        - Gender: {gender}
        
        Link to evaluate:
        - URL: {link_url}
        - Link Text: {link_text}
        - Page Context: {page_context[:500] if page_context else 'No context available'}
        
        Determine:
        1. Is this link relevant for student housing? (true/false)
        2. What is the relevance score? (0-100)
        3. What is your reasoning?
        
        Return your analysis as JSON:
        {{
            "is_relevant": boolean,
            "relevance_score": number (0-100),
            "reasoning": "string explaining your analysis"
        }}
        """
        
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at evaluating links for student housing relevance. Always return valid JSON."
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        content = response.choices[0].message.content.strip()
        
        try:
            analysis = json.loads(content)
            return analysis
        except json.JSONDecodeError as e:
            print(f"LLM link evaluation parsing failed: {e}")
            return {
                "is_relevant": False,
                "relevance_score": 0,
                "reasoning": f"Failed to parse LLM response: {e}"
            }
            
    except Exception as e:
        print(f"LLM link evaluation failed: {e}")
        return {
            "is_relevant": False,
            "relevance_score": 0,
            "reasoning": f"LLM evaluation failed: {e}"
        }

class DeepSearchTracker:
    """Tracks all visited links and shortlisted links for deep search"""
    
    def __init__(self):
        self.visited_links: Set[str] = set()
        self.shortlisted_links: Set[str] = set()
        self.link_evaluations: Dict[str, Dict] = {}
        self.search_depth = 0
        self.max_depth = 3  # Maximum depth to prevent infinite loops
    
    def add_visited(self, url: str, reason: str = ""):
        """Add a link to visited list"""
        self.visited_links.add(url)
        if reason:
            self.link_evaluations[url] = {"reason": reason, "timestamp": time.time()}
    
    def add_shortlisted(self, url: str, reason: str = ""):
        """Add a link to shortlisted list"""
        self.shortlisted_links.add(url)
        if url in self.link_evaluations:
            self.link_evaluations[url]["shortlisted"] = True
            self.link_evaluations[url]["shortlist_reason"] = reason
        else:
            self.link_evaluations[url] = {
                "shortlisted": True, 
                "shortlist_reason": reason, 
                "timestamp": time.time()
            }
    
    def get_report(self) -> Dict:
        """Get a comprehensive report of all links"""
        return {
            "total_visited": len(self.visited_links),
            "total_shortlisted": len(self.shortlisted_links),
            "visited_links": list(self.visited_links),
            "shortlisted_links": list(self.shortlisted_links),
            "evaluations": self.link_evaluations,
            "search_depth": self.search_depth
        }

async def evaluate_link_relevance(url: str, link_text: str, page_content: str, params: Dict) -> Tuple[bool, str]:
    """
    Evaluate if a link is worth following using LLM intelligence only
    Returns (is_relevant, reason)
    """
    try:
        # Use LLM to evaluate the link (no fallback)
        analysis = await evaluate_link_with_llm(url, link_text, page_content, params)
        
        is_relevant = analysis.get('is_relevant', False)
        reasoning = analysis.get('reasoning', 'No reasoning provided')
        
        return is_relevant, reasoning
        
    except Exception as e:
        print(f"LLM link evaluation failed: {e}")
        raise Exception(f"LLM link evaluation failed: {e}")


async def verify_listing_with_playwright(url, params, page=None):
    """Extract real listing data from the actual URL"""
    print(f"Visiting: {url}")
    
    # If no page provided, create a new browser instance (fallback)
    if page is None:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
            headless=False,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
            )
            page = await browser.new_page()
            try:
                print(f"Browser launched successfully. Navigating to: {url}")
                await page.goto(url, wait_until='domcontentloaded')
                print("Page loaded successfully. Extracting listing data...")
                await asyncio.sleep(2)
                return await _extract_listing_data(page, url, params)
            finally:
                await browser.close()
    else:
        # Use existing page (much faster)
        try:
            print(f"Using existing browser. Navigating to: {url}")
            await page.goto(url, wait_until='domcontentloaded')  # No timeout
            print("Page loaded successfully. Extracting listing data...")
            await asyncio.sleep(1)  # Reduced sleep time
            return await _extract_listing_data(page, url, params)
        except Exception as e:
            print(f"Error using existing page: {e}")
            return None

async def _extract_listing_data(page, url, params):
    """Extract listing data from the current page"""
    try:
            # Extract real listing data using JavaScript
            listing_data = await page.evaluate("""
                () => {
                    const data = {};
                    
                    // Extract title - try multiple approaches
                    const titleSelectors = [
                        'h1', 'h2', 'h3', 
                        '[class*="title"]', '[class*="heading"]',
                        '[class*="listing"]', '[class*="property"]'
                    ];
                    
                    for (const selector of titleSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            data.title = element.textContent.trim();
                            break;
                        }
                    }
                    
                    // Extract price - try multiple approaches
                    const pricePatterns = [
                        /\\$?([0-9,]+)\\s*(?:per\\s*month|\\/month|monthly|rent)/i,
                        /\\$?([0-9,]+)\\s*(?:CAD|USD)?/i,
                        /rent[^$]*\\$?([0-9,]+)/i,
                        /([0-9,]+)\\s*\\$/
                    ];
                    
                    const pageText = document.body.innerText;
                    for (const pattern of pricePatterns) {
                        const match = pageText.match(pattern);
                        if (match) {
                            const price = parseInt(match[1].replace(/,/g, ''));
                            if (price >= 400 && price <= 2000) {
                                data.price = price;
                                break;
                            }
                        }
                    }
                    
                    // Extract location - try multiple approaches
                    const locationPatterns = [
                        /(?:in|at|near)\\s+([A-Za-z\\s]+(?:Street|Ave|Road|Drive|Lane|Boulevard))/i,
                        /(?:location|address)[^\\n]*([A-Za-z\\s]+(?:Street|Ave|Road|Drive|Lane|Boulevard))/i,
                        /(Columbia|Lester|Keats|University|Waterloo|Kitchener)/i
                    ];
                    
                    for (const pattern of locationPatterns) {
                        const match = pageText.match(pattern);
                        if (match) {
                            data.location = match[1].trim();
                            break;
                        }
                    }
                    
                    // Extract description
                    const descSelectors = [
                        '[class*="description"]',
                        '[class*="details"]',
                        '[class*="content"]',
                        'p',
                        'div[class*="text"]'
                    ];
                    
                    for (const selector of descSelectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.textContent.trim();
                            if (text.length > 50 && text.length < 1000) {
                                data.description = text;
                                break;
                            }
                        }
                        if (data.description) break;
                    }
                    
                    // Check for housing-related keywords
                    const housingKeywords = [
                        'rent', 'lease', 'apartment', 'room', 'housing', 'accommodation',
                        'student housing', 'furnished', 'unfurnished', 'available',
                        'for rent', 'rental', 'sublet', 'sublease'
                    ];
                    
                    const hasHousingKeywords = housingKeywords.some(keyword => 
                        pageText.toLowerCase().includes(keyword)
                    );
                    
                    data.isHousingRelated = hasHousingKeywords;
                    
                    return data;
                }
            """)
            
            # Only proceed if it's housing-related and has a title
            if not listing_data.get('isHousingRelated', False) or not listing_data.get('title'):
                print(f"Not a housing listing or no title found for: {url}")
                return None
            
            # Determine source from URL
            source = get_source_from_url(url)
            
            result = {
                'title': listing_data.get('title', 'Housing Listing'),
                'price': listing_data.get('price'),
                'location': listing_data.get('location', 'Waterloo'),
                'description': listing_data.get('description', ''),
                'source': source,
                'url': url
            }
            
            print(f"Extracted listing: {result['title']} - ${result.get('price', 'N/A')}")
            return result
            
    except Exception as e:
        print(f"Failed to extract data from {url}: {e}")
        return None

def get_source_from_url(url: str) -> str:
    """Determine source from URL"""
    from urllib.parse import urlparse
    domain = urlparse(url).netloc.lower()
    
    if 'kijiji' in domain:
        return 'Kijiji'
    elif 'facebook' in domain:
        return 'Facebook Marketplace'
    elif 'craigslist' in domain:
        return 'Craigslist'
    elif 'rentals.ca' in domain:
        return 'Rentals.ca'
    elif 'rentfaster' in domain:
        return 'RentFaster'
    elif 'rentboard' in domain:
        return 'RentBoard'
    elif 'reddit' in domain:
        return 'Reddit'
    elif 'uwaterloo' in domain:
        return 'UW Off-Campus Housing'
    else:
        return 'Google Search'

# Replace the old verify_listing with the new one
verify_listing = verify_listing_with_playwright

class GooglePlaywrightScraper:
    """Advanced Google search scraper using Playwright with deep search capabilities"""
    
    def __init__(self, enable_deep_search: bool = True):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.visited_urls: Set[str] = set()
        self.enable_deep_search = enable_deep_search
        self.tracker = DeepSearchTracker() if enable_deep_search else None
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        ]
        
        # Search queries to try
        self.search_queries = [
            "waterloo student housing rent apartment room",
            "kitchener waterloo student housing for rent",
            "UW student housing Columbia Lester",
            "waterloo university student apartment rental",
            "kitchener waterloo student room for rent",
            "UW off campus housing student rental",
            "waterloo student housing furnished",
            "kitchener waterloo student apartment lease"
        ]
        
        # Keywords that indicate housing listings
        self.housing_keywords = [
            "rent", "lease", "apartment", "room", "housing", "accommodation",
            "student housing", "furnished", "unfurnished", "available",
            "for rent", "rental", "sublet", "sublease"
        ]
        
        # Keywords that indicate student housing
        self.student_keywords = [
            "student", "university", "UW", "waterloo", "college",
            "campus", "academic", "semester", "term"
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()
    
    async def start_browser(self):
        """Start the browser"""
        print("Starting Playwright browser...")
        self.playwright = await async_playwright().start()
        
        # Try visible mode first, fallback to headless if it fails (for HTTP API compatibility)
        try:
            print("Launching Chromium browser (visible mode)...")
            self.browser = await self.playwright.chromium.launch(
                headless=False,  # Use visible mode for better stealth
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            print("Visible mode browser launched successfully")
        except Exception as e:
            print(f"Visible mode failed: {e}")
            print("Falling back to headless mode for HTTP API compatibility...")
            self.browser = await self.playwright.chromium.launch(
                headless=True,  # Fallback to headless mode
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )
            print("Headless mode browser launched successfully")
        
        print("Creating new page...")
        self.page = await self.browser.new_page()
        await self.page.set_extra_http_headers({
            'User-Agent': random.choice(self.user_agents)
        })
        print("Browser setup complete!")
    
    async def close_browser(self):
        """Close the browser"""
        if self.page:
            await self.page.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def search_google(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Search Google and extract results from multiple pages"""
        results = []
        
        try:
            for page_num in range(max_pages):
                start_index = page_num * 10
                search_url = f"https://www.google.com/search?q={query}&start={start_index}"
                
                logger.info(f"Searching Google page {page_num + 1} for: {query}")
                
                print(f"Navigating to Google search: {search_url}")
                await self.page.goto(search_url, wait_until='networkidle')
                print("Search page loaded. Waiting 5 seconds so you can see the browser...")
                await asyncio.sleep(2)  # Reduced delay for faster search
                
                # Extract search results (excluding ads)
                page_results = await self.extract_search_results()
                results.extend(page_results)
                
                logger.info(f"Found {len(page_results)} results on page {page_num + 1}")
                
                # Check if there are more pages
                if not await self.has_next_page():
                    break
                    
        except Exception as e:
            logger.error(f"Error searching Google: {e}")
        
        return results
    
    async def extract_search_results(self) -> List[Dict]:
        results = []
        try:
            # Wait for the main search container
            await self.page.wait_for_selector('div#search, div#rso')
            # Check for bot detection/captcha
            page_text = await self.page.content()
            if ("unusual traffic" in page_text or "detected unusual traffic" in page_text or "Our systems have detected" in page_text):
                logger.warning("Google is showing a CAPTCHA or bot detection page.")
                return results

            # Find all organic result links with a title
            anchors = await self.page.query_selector_all('a:has(h3)')
            logger.info(f"Found {len(anchors)} anchor elements with h3 children")
            for anchor in anchors:
                try:
                    href = await anchor.get_attribute('href')
                    if not href or not href.startswith('http'):
                        continue
                    # Filter out Google internal links
                    if 'google.' in href or '/search?' in href or '/url?' in href:
                        continue
                    h3 = await anchor.query_selector('h3')
                    title = await h3.inner_text() if h3 else None
                    if not title or len(title.strip()) < 5:
                        continue
                    # Try to get a snippet (the next sibling div, or parent div)
                    snippet = ""
                    parent = await anchor.evaluate_handle('node => node.parentElement')
                    if parent:
                        snippet_div = await parent.query_selector('div')
                        if snippet_div:
                            snippet = await snippet_div.inner_text()
                    if self.is_housing_related(title, snippet):
                        print(f"Found housing result: {title[:50]}... -> {href}")
                        results.append({
                            'title': title.strip(),
                            'url': href,
                            'snippet': snippet.strip(),
                            'source': 'Google Search'
                        })
                except Exception as e:
                    logger.debug(f"Error extracting anchor result: {e}")
                    continue
        except Exception as e:
            logger.error(f"Error extracting search results: {e}")
        logger.info(f"Successfully extracted {len(results)} housing-related results")
        return results
    
    async def has_next_page(self) -> bool:
        """Check if there's a next page"""
        try:
            next_button = await self.page.query_selector('a#pnnext')
            return next_button is not None
        except:
            return False
    
    def is_housing_related(self, title: str, snippet: str) -> bool:
        """Check if the result is housing-related"""
        text = (title + " " + snippet).lower()
        
        # Check for housing keywords
        has_housing_keywords = any(keyword in text for keyword in self.housing_keywords)
        
        # Check for student keywords
        has_student_keywords = any(keyword in text for keyword in self.student_keywords)
        
        # Must have housing keywords, preferably also student keywords
        return has_housing_keywords
    
    async def extract_listing_info(self, title: str, url: str) -> Optional[Dict]:
        """Extract listing information from page content"""
        try:
            # Use JavaScript to extract information
            listing_data = await self.page.evaluate("""
                () => {
                    const data = {};
                    
                    // Extract price - try multiple approaches
                    const pricePatterns = [
                        /\\$?([0-9,]+)\\s*(?:per\\s*month|\\/month|monthly|rent)/i,
                        /\\$?([0-9,]+)\\s*(?:CAD|USD)?/i,
                        /rent[^$]*\\$?([0-9,]+)/i,
                        /([0-9,]+)\\s*\\$/
                    ];
                    
                    const pageText = document.body.innerText;
                    for (const pattern of pricePatterns) {
                        const match = pageText.match(pattern);
                        if (match) {
                            const price = parseInt(match[1].replace(/,/g, ''));
                            if (price >= 400 && price <= 2000) {
                                data.price = price;
                                break;
                            }
                        }
                    }
                    
                    // Extract location - try multiple approaches
                    const locationPatterns = [
                        /(?:in|at|near)\\s+([A-Za-z\\s]+(?:Street|Ave|Road|Drive|Lane|Boulevard))/i,
                        /(?:location|address)[^\\n]*([A-Za-z\\s]+(?:Street|Ave|Road|Drive|Lane|Boulevard))/i,
                        /(Columbia|Lester|Keats|University|Waterloo|Kitchener)/i
                    ];
                    
                    for (const pattern of locationPatterns) {
                        const match = pageText.match(pattern);
                        if (match) {
                            data.location = match[1].trim();
                            break;
                        }
                    }
                    
                    // Extract description
                    const descSelectors = [
                        '[class*="description"]',
                        '[class*="details"]',
                        '[class*="content"]',
                        'p',
                        'div[class*="text"]'
                    ];
                    
                    for (const selector of descSelectors) {
                        const elements = document.querySelectorAll(selector);
                        for (const element of elements) {
                            const text = element.textContent.trim();
                            if (text.length > 50 && text.length < 1000) {
                                data.description = text;
                                break;
                            }
                        }
                        if (data.description) break;
                    }
                    
                    // Check for housing-related keywords
                    const housingKeywords = [
                        'rent', 'lease', 'apartment', 'room', 'housing', 'accommodation',
                        'student housing', 'furnished', 'unfurnished', 'available',
                        'for rent', 'rental', 'sublet', 'sublease'
                    ];
                    
                    const hasHousingKeywords = housingKeywords.some(keyword => 
                        pageText.toLowerCase().includes(keyword)
                    );
                    
                    data.isHousingRelated = hasHousingKeywords;
                    
                    return data;
                }
            """)
            
            # Only proceed if it's housing-related
            if not listing_data.get('isHousingRelated', False):
                return None
            
            # Determine source from URL
            source = self.get_source_from_url(url)
            
            return {
                'title': title,
                'price': listing_data.get('price'),
                'location': listing_data.get('location', 'Waterloo'),
                'description': listing_data.get('description', ''),
                'source': source,
                'url': url
            }
            
        except Exception as e:
            logger.debug(f"Error extracting listing info: {e}")
            return None
    
    def get_source_from_url(self, url: str) -> str:
        """Determine source from URL"""
        domain = urlparse(url).netloc.lower()
        
        if 'kijiji' in domain:
            return 'Kijiji'
        elif 'facebook' in domain:
            return 'Facebook Marketplace'
        elif 'craigslist' in domain:
            return 'Craigslist'
        elif 'rentals.ca' in domain:
            return 'Rentals.ca'
        elif 'rentfaster' in domain:
            return 'RentFaster'
        elif 'rentboard' in domain:
            return 'RentBoard'
        elif 'reddit' in domain:
            return 'Reddit'
        elif 'uwaterloo' in domain:
            return 'UW Off-Campus Housing'
        else:
            return 'Google Search'
    
    def matches_criteria(self, listing: Dict, params: Dict) -> bool:
        """Check if listing matches search criteria"""
        title_lower = listing.get('title', '').lower()
        description_lower = listing.get('description', '').lower()
        location_lower = listing.get('location', '').lower()
        
        # Price filter
        if listing.get('price'):
            if params.get('price_min') and listing['price'] < params['price_min']:
                return False
            if params.get('price_max') and listing['price'] > params['price_max']:
                return False
        
        # Location filter
        if params.get('location'):
            location_keywords = params['location'].lower().split()
            if not any(keyword in location_lower for keyword in location_keywords):
                return False
        
        # Term filter
        if params.get('term'):
            term_lower = params['term'].lower()
            if term_lower not in title_lower and term_lower not in description_lower:
                return False
        
        # Furnished filter
        if params.get('furnished') is not None:
            furnished_keywords = ['furnished', 'furniture', 'fully furnished']
            is_furnished = any(keyword in title_lower or keyword in description_lower 
                             for keyword in furnished_keywords)
            if params['furnished'] != is_furnished:
                return False
        
        # Lease type filter
        if params.get('lease_type'):
            lease_type_lower = params['lease_type'].lower()
            if lease_type_lower not in title_lower and lease_type_lower not in description_lower:
                return False
        
        return True
    
    async def extract_links_from_page(self, url: str, params: Dict) -> List[Dict]:
        """Extract and evaluate links from a page for deep search using LLM intelligence"""
        if not self.enable_deep_search or not self.tracker:
            return []
        
        try:
            print(f"Extracting links from: {url}")
            await self.page.goto(url, wait_until='domcontentloaded')
            await asyncio.sleep(2)  # Let page load
            
            # Get page content for evaluation
            page_content = await self.page.content()
            
            # Use LLM to analyze the page and extract relevant links
            print(f"Using LLM to analyze page content: {url}")
            analysis = await evaluate_page_with_llm(url, page_content, params)
            
            if analysis.get('is_relevant', False):
                print(f"Page is relevant: {analysis.get('reasoning', 'No reasoning')}")
            
            # Extract all links
            links = await self.page.evaluate("""
                () => {
                    const links = [];
                    const anchors = document.querySelectorAll('a[href]');
                    
                    for (const anchor of anchors) {
                        const href = anchor.getAttribute('href');
                        const text = anchor.textContent.trim();
                        
                        if (href && text && href.startsWith('http')) {
                            links.push({
                                url: href,
                                text: text,
                                title: anchor.getAttribute('title') || ''
                            });
                        }
                    }
                    
                    return links;
                }
            """)
            
            print(f"Found {len(links)} links on {url}")
            
            # Pre-filter links using keywords before LLM evaluation
            housing_keywords = [
                'rent', 'lease', 'apartment', 'room', 'housing', 'accommodation',
                'student housing', 'furnished', 'unfurnished', 'available',
                'for rent', 'rental', 'sublet', 'sublease', 'waterloo', 'kitchener',
                'university', 'campus', 'student', 'private', 'shared'
            ]
            
            # Filter links that might be relevant based on text content
            potential_links = []
            for link in links:
                link_text_lower = link['text'].lower()
                if any(keyword in link_text_lower for keyword in housing_keywords):
                    potential_links.append(link)
            
            # If we have too many potential links, prioritize by keyword density
            if len(potential_links) > 15:
                potential_links.sort(key=lambda x: sum(1 for keyword in housing_keywords if keyword in x['text'].lower()), reverse=True)
                potential_links = potential_links[:15]
            
            # Evaluate each link using LLM
            relevant_links = []
            for link in potential_links:
                link_url = link['url']
                link_text = link['text']
                
                # Skip if already visited
                if link_url in self.visited_urls:
                    continue
                
                # Use LLM to evaluate link relevance
                link_analysis = await evaluate_link_with_llm(link_url, link_text, page_content, params)
                
                if link_analysis.get('is_relevant', False):
                    reason = link_analysis.get('reasoning', 'LLM determined relevance')
                    print(f"Shortlisted: {link_text[:50]}... - {reason}")
                    self.tracker.add_shortlisted(link_url, reason)
                    relevant_links.append({
                        'url': link_url,
                        'text': link_text,
                        'reason': reason
                    })
                else:
                    reason = link_analysis.get('reasoning', 'LLM determined not relevant')
                    print(f"Skipped: {link_text[:50]}... - {reason}")
            
            return relevant_links
            
        except Exception as e:
            print(f"Error extracting links from {url}: {e}")
            return []
    
    async def deep_search_listing(self, url: str, params: Dict) -> Optional[Dict]:
        """Perform deep search on a specific listing URL"""
        if not self.enable_deep_search or not self.tracker:
            return await verify_listing_with_playwright(url, params, self.page)
        
        try:
            print(f"Deep searching: {url}")
            self.tracker.add_visited(url, "deep search listing")
            
            # First, verify the listing
            listing = await verify_listing_with_playwright(url, params, self.page)
            
            if listing:
                self.tracker.add_shortlisted(url, "valid housing listing")
                
                # Extract additional links from this page
                additional_links = await self.extract_links_from_page(url, params)
                
                # Add any additional findings to the listing
                if additional_links:
                    listing['related_links'] = additional_links
                    print(f"Found {len(additional_links)} related links on this page")
            
            return listing
            
        except Exception as e:
            print(f"Error in deep search for {url}: {e}")
            return None
    
    async def search_duckduckgo(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Search DuckDuckGo and extract results from multiple pages"""
        results = []
        try:
            for page_num in range(max_pages):
                search_url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
                if page_num > 0:
                    search_url += f"&s={page_num * 30}"
                logger.info(f"Searching DuckDuckGo page {page_num + 1} for: {query}")
                print(f"Navigating to DuckDuckGo search: {search_url}")
                await self.page.goto(search_url, wait_until='networkidle')
                print("DuckDuckGo page loaded. Waiting 5 seconds so you can see the browser...")
                await asyncio.sleep(2)
                page_results = await self.extract_duckduckgo_results()
                results.extend(page_results)
                logger.info(f"Found {len(page_results)} results on DuckDuckGo page {page_num + 1}")
                # DuckDuckGo loads more results via infinite scroll, so break if less than 30 results
                if len(page_results) < 30:
                    break
        except Exception as e:
            logger.error(f"Error searching DuckDuckGo: {e}")
        return results

    async def extract_duckduckgo_results(self) -> List[Dict]:
        import os
        results = []
        try:
            # Wait for results to appear, retrying if necessary
            max_wait_time = 15  # seconds
            poll_interval = 1   # seconds
            waited = 0
            found = False
            while waited < max_wait_time:
                elements = await self.page.query_selector_all('a[data-testid="result-title-a"]')
                if elements and len(elements) > 0:
                    found = True
                    break
                await asyncio.sleep(poll_interval)
                waited += poll_interval
            if not found:
                print(f"DuckDuckGo: No result links found after {max_wait_time} seconds. Dumping HTML for debugging.")
                html = await self.page.content()
                abs_path = os.path.abspath('duckduckgo_debug.html')
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(html)
                    f.flush()
                    os.fsync(f.fileno())
                print(f"Saved DuckDuckGo HTML to {abs_path}")
                return results

            # Use the best selector for actual extraction
            result_elements = await self.page.query_selector_all('a[data-testid="result-title-a"]')
            print(f"Found {len(result_elements)} DuckDuckGo result elements with a[data-testid='result-title-a']")
            for element in result_elements:
                try:
                    title = await element.inner_text()
                    if not title or len(title.strip()) < 5:
                        continue
                    href = await element.get_attribute('href')
                    if not href or not href.startswith('http'):
                        continue
                    # Try to get a snippet (parent div)
                    snippet = ""
                    parent = await element.evaluate_handle('node => node.parentElement')
                    if parent:
                        snippet_div = await parent.query_selector('div')
                        if snippet_div:
                            snippet = await snippet_div.inner_text()
                    if self.is_housing_related(title, snippet):
                        print(f"Found DuckDuckGo housing result: {title[:50]}... -> {href}")
                        results.append({
                            'title': title.strip(),
                            'url': href,
                            'snippet': snippet.strip(),
                            'source': 'DuckDuckGo Search'
                        })
                except Exception as e:
                    print(f"Error extracting DuckDuckGo result: {e}")
                    continue
        except Exception as e:
            print(f"Error extracting DuckDuckGo results: {e}")
        print(f"Successfully extracted {len(results)} DuckDuckGo housing-related results")
        return results

    async def build_search_queries_from_params(self, params: Dict) -> List[str]:
        """Build custom search queries using LLM intelligence only"""
        
        # Use LLM-generated queries (no fallback)
        print("Generating intelligent search queries with LLM...")
        llm_queries = await generate_llm_search_queries(params)
        return llm_queries
        
    async def calculate_listing_score(self, listing: Dict, params: Dict) -> float:
        """Calculate relevance score for a listing using LLM intelligence"""
        try:
            # Use LLM to score the listing
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
            # Extract key parameters
            location = params.get('location', 'Waterloo')
            price_min = params.get('price_min', 400)
            price_max = params.get('price_max', 1500)
            term = params.get('term', '')
            furnished = params.get('furnished')
            lease_type = params.get('lease_type', '')
            gender = params.get('gender', 'Any')
            
            context = f"""
            You are an intelligent housing search agent. Score this listing for relevance to the user's requirements.
            
            User Requirements:
            - Location: {location}
            - Price Range: ${price_min}-${price_max}
            - Term: {term if term else 'Any'}
            - Furnished: {'Yes' if furnished else 'No' if furnished is False else 'Any'}
            - Lease Type: {lease_type if lease_type else 'Any'}
            - Gender: {gender}
            
            Listing to score:
            - Title: {listing.get('title', 'No title')}
            - Price: {listing.get('price', 'Not specified')}
            - Location: {listing.get('location', 'Not specified')}
            - Description: {listing.get('description', 'No description')[:500]}
            - URL: {listing.get('url', 'No URL')}
            
            Score this listing from 0-100 based on how well it matches the user's requirements.
            Consider: price match, location relevance, term alignment, furnished preference, lease type, and overall quality.
            
            Return only a JSON object with the score and reasoning:
            {{
                "score": number (0-100),
                "reasoning": "string explaining the score"
            }}
            """
            
            response = await client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert at scoring housing listings for relevance. Always return valid JSON."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                max_tokens=200,
                temperature=0.3
            )
            
            content = response.choices[0].message.content.strip()
            
            try:
                analysis = json.loads(content)
                score = analysis.get('score', 0)
                reasoning = analysis.get('reasoning', 'No reasoning provided')
                print(f"LLM Listing Score: {score}/100 - {reasoning}")
                return float(score)
            except json.JSONDecodeError as e:
                print(f"LLM scoring parsing failed: {e}")
                return 0.0
                
        except Exception as e:
            print(f"LLM listing scoring failed: {e}")
            # No fallback - LLM is required for intelligent scoring
            raise Exception(f"LLM listing scoring failed: {e}")
    
    async def search_with_multiple_queries(self, params: Dict, max_queries: int = 5, progress_callback=None) -> List[Dict]:
        all_results = []
        queries_to_try = await self.build_search_queries_from_params(params)
        queries_to_try = queries_to_try[:max_queries]
        
        print(f"Generated {len(queries_to_try)} custom search queries based on your parameters:")
        for i, query in enumerate(queries_to_try, 1):
            print(f"  {i}. {query}")
        print()
        
        # Send initial progress
        if progress_callback:
            await progress_callback({
                "type": "progress",
                "message": f"Starting search with {len(queries_to_try)} queries...",
                "step": "search_start",
                "progress": 10
            })
        
        for i, query in enumerate(queries_to_try):
            logger.info(f"Trying search query {i + 1}: {query}")
            print(f"Searching: {query}")
            
            # Send query progress
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "message": f"Searching query {i + 1}/{len(queries_to_try)}: {query}",
                    "step": "query_search",
                    "progress": 20 + (i * 20)
                })
            
            # Try DuckDuckGo first
            try:
                search_results = await self.search_duckduckgo(query, max_pages=2)
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed, falling back to Google: {e}")
                search_results = []
            # If DuckDuckGo fails or returns no results, try Google
            if not search_results:
                logger.info("Trying Google fallback...")
                try:
                    search_results = await self.search_google(query, max_pages=2)
                except Exception as e:
                    logger.warning(f"Google search also failed: {e}")
                    search_results = []
            
            # Process results concurrently
            if search_results:
                if progress_callback:
                    await progress_callback({
                        "type": "progress",
                        "message": f"Found {len(search_results)} results, processing listings...",
                        "step": "processing",
                        "progress": 30 + (i * 20)
                    })
                
                # Process up to 5 results concurrently
                tasks = []
                for result in search_results[:5]:
                    if len(all_results) >= 50:  # Increased back to 50
                        break
                    
                    if self.enable_deep_search and self.tracker:
                        task = self.deep_search_listing_concurrent(result['url'], params, progress_callback)
                    else:
                        task = self.verify_listing_concurrent(result['url'], params, progress_callback)
                    tasks.append(task)
                
                # Wait for all tasks to complete
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, dict) and result:
                            all_results.append(result)
            
            if i < len(queries_to_try) - 1:
                await asyncio.sleep(random.uniform(3, 6))
        
        # Sort results by relevance score (highest to lowest)
        all_results.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        print(f"\nSorted {len(all_results)} results by relevance score:")
        for i, result in enumerate(all_results[:10], 1):  # Show top 10
            score = result.get('relevance_score', 0)
            title = result.get('title', 'No title')[:50]
            price = result.get('price', 'N/A')
            print(f"  {i:2d}. Score: {score:5.1f} | {title}... | ${price}")
        
        return all_results

    async def deep_search_listing_concurrent(self, url: str, params: Dict, progress_callback=None) -> Optional[Dict]:
        """Concurrent version of deep search that sends real-time updates"""
        if not self.enable_deep_search or not self.tracker:
            return await self.verify_listing_concurrent(url, params, progress_callback)
        
        try:
            print(f"Deep searching: {url}")
            self.tracker.add_visited(url, "deep search listing")
            
            # Send progress update
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "message": f"Deep searching: {url[:50]}...",
                    "step": "deep_search",
                    "progress": 50
                })
            
            # First, verify the listing
            listing = await verify_listing_with_playwright(url, params, self.page)
            
            if listing:
                self.tracker.add_shortlisted(url, "valid housing listing")
                
                # Send listing found update
                if progress_callback:
                    await progress_callback({
                        "type": "listing_found",
                        "message": f"Found listing: {listing.get('title', 'No title')[:50]}...",
                        "step": "listing_found",
                        "progress": 60,
                        "listing": listing
                    })
                
                # Extract additional links from this page
                additional_links = await self.extract_links_from_page(url, params)
                
                # Add any additional findings to the listing
                if additional_links:
                    listing['related_links'] = additional_links
                    print(f"Found {len(additional_links)} related links on this page")
                    
                    # Send subpage exploration update
                    if progress_callback:
                        await progress_callback({
                            "type": "progress",
                            "message": f"Exploring {len(additional_links)} related links...",
                            "step": "subpage_exploration",
                            "progress": 70
                        })
                    
                    # Explore the most promising subpages for additional listings
                    await self.explore_subpages_for_listings(additional_links, params, progress_callback)
            
            return listing
            
        except Exception as e:
            print(f"Error in deep search for {url}: {e}")
            return None
    
    async def verify_listing_concurrent(self, url: str, params: Dict, progress_callback=None) -> Optional[Dict]:
        """Concurrent version of listing verification that sends real-time updates"""
        try:
            print(f"Verifying listing: {url}")
            
            # Send progress update
            if progress_callback:
                await progress_callback({
                    "type": "progress",
                    "message": f"Verifying listing: {url[:50]}...",
                    "step": "verification",
                    "progress": 55
                })
            
            # Verify the listing
            listing = await verify_listing_with_playwright(url, params, self.page)
            
            if listing:
                # Calculate relevance score using LLM
                score = await self.calculate_listing_score(listing, params)
                listing['relevance_score'] = score
                
                # Send listing found update
                if progress_callback:
                    await progress_callback({
                        "type": "listing_found",
                        "message": f"Found listing: {listing.get('title', 'No title')[:50]}... (Score: {score:.1f})",
                        "step": "listing_found",
                        "progress": 60,
                        "listing": listing
                    })
            
            return listing
            
        except Exception as e:
            print(f"Error verifying listing {url}: {e}")
            return None
    
    async def explore_subpages_for_listings(self, links: List[Dict], params: Dict, progress_callback=None) -> List[Dict]:
        """Explore subpages to find additional listings"""
        additional_listings = []
        
        # Limit to top 3 most promising links for efficiency
        promising_links = links[:3]
        
        for link in promising_links:
            try:
                url = link['url']
                text = link['text']
                
                # Skip if already visited
                if url in self.visited_urls:
                    continue
                
                print(f"Exploring subpage: {text[:50]}...")
                
                # Send progress update
                if progress_callback:
                    await progress_callback({
                        "type": "progress",
                        "message": f"Exploring subpage: {text[:50]}...",
                        "step": "subpage_exploration",
                        "progress": 75
                    })
                
                # Visit the subpage
                await self.page.goto(url, wait_until='domcontentloaded')
                await asyncio.sleep(2)
                
                # Check if this page contains individual listings
                page_content = await self.page.content()
                
                # Look for listing patterns in the page
                listing_indicators = await self.page.evaluate("""
                    () => {
                        const indicators = {
                            hasPrice: false,
                            hasTitle: false,
                            hasDescription: false,
                            listingCount: 0
                        };
                        
                        // Check for price patterns
                        const pricePatterns = [
                            /\\$[0-9,]+/g,
                            /[0-9,]+\\s*(?:per\\s*month|\\/month|monthly)/gi
                        ];
                        
                        const pageText = document.body.innerText;
                        for (const pattern of pricePatterns) {
                            if (pattern.test(pageText)) {
                                indicators.hasPrice = true;
                                break;
                            }
                        }
                        
                        // Check for title patterns
                        const titleSelectors = ['h1', 'h2', 'h3', '[class*="title"]', '[class*="listing"]'];
                        for (const selector of titleSelectors) {
                            if (document.querySelector(selector)) {
                                indicators.hasTitle = true;
                                break;
                            }
                        }
                        
                        // Check for description patterns
                        const descSelectors = ['p', '[class*="description"]', '[class*="details"]'];
                        for (const selector of descSelectors) {
                            if (document.querySelector(selector)) {
                                indicators.hasDescription = true;
                                break;
                            }
                        }
                        
                        // Count potential listings (elements with price-like content)
                        const priceElements = document.querySelectorAll('*');
                        for (const element of priceElements) {
                            const text = element.textContent || '';
                            if (/\\$[0-9,]+/.test(text) && text.length < 200) {
                                indicators.listingCount++;
                            }
                        }
                        
                        return indicators;
                    }
                """)
                
                # If this looks like a listings page, extract individual listings
                if (listing_indicators['hasPrice'] and 
                    (listing_indicators['hasTitle'] or listing_indicators['hasDescription']) and
                    listing_indicators['listingCount'] > 0):
                    
                    print(f"Found potential listings page with {listing_indicators['listingCount']} listings")
                    
                    # Extract individual listings from this page
                    page_listings = await self.extract_listings_from_page(url, params)
                    
                    for listing in page_listings:
                        if listing:
                            # Calculate relevance score
                            score = await self.calculate_listing_score(listing, params)
                            listing['relevance_score'] = score
                            additional_listings.append(listing)
                            
                            # Send listing found update
                            if progress_callback:
                                await progress_callback({
                                    "type": "listing_found",
                                    "message": f"Found additional listing: {listing.get('title', 'No title')[:50]}...",
                                    "step": "subpage_listing_found",
                                    "progress": 80,
                                    "listing": listing
                                })
                
                # Mark as visited
                self.visited_urls.add(url)
                
            except Exception as e:
                print(f"Error exploring subpage {link.get('url', 'unknown')}: {e}")
                continue
        
        return additional_listings
    
    async def extract_listings_from_page(self, url: str, params: Dict) -> List[Dict]:
        """Extract individual listings from a listings page"""
        try:
            # Extract listings using JavaScript
            listings = await self.page.evaluate("""
                () => {
                    const listings = [];
                    
                    // Look for common listing patterns
                    const listingSelectors = [
                        '[class*="listing"]',
                        '[class*="property"]',
                        '[class*="item"]',
                        '[class*="card"]',
                        'article',
                        '.result',
                        '.search-result'
                    ];
                    
                    for (const selector of listingSelectors) {
                        const elements = document.querySelectorAll(selector);
                        
                        for (const element of elements) {
                            const listing = {};
                            
                            // Extract title
                            const titleSelectors = ['h1', 'h2', 'h3', 'h4', '[class*="title"]', '[class*="heading"]'];
                            for (const titleSelector of titleSelectors) {
                                const titleEl = element.querySelector(titleSelector);
                                if (titleEl && titleEl.textContent.trim()) {
                                    listing.title = titleEl.textContent.trim();
                                    break;
                                }
                            }
                            
                            // Extract price
                            const pricePatterns = [
                                /\\$?([0-9,]+)\\s*(?:per\\s*month|\\/month|monthly|rent)/i,
                                /\\$?([0-9,]+)\\s*(?:CAD|USD)?/i,
                                /rent[^$]*\\$?([0-9,]+)/i
                            ];
                            
                            const text = element.textContent || '';
                            for (const pattern of pricePatterns) {
                                const match = text.match(pattern);
                                if (match) {
                                    const price = parseInt(match[1].replace(/,/g, ''));
                                    if (price >= 400 && price <= 2000) {
                                        listing.price = price;
                                        break;
                                    }
                                }
                            }
                            
                            // Extract location
                            const locationPatterns = [
                                /(?:in|at|near)\\s+([A-Za-z\\s]+(?:Street|Ave|Road|Drive|Lane|Boulevard))/i,
                                /(Columbia|Lester|Keats|University|Waterloo|Kitchener)/i
                            ];
                            
                            for (const pattern of locationPatterns) {
                                const match = text.match(pattern);
                                if (match) {
                                    listing.location = match[1].trim();
                                    break;
                                }
                            }
                            
                            // Extract description
                            const descSelectors = ['p', '[class*="description"]', '[class*="details"]'];
                            for (const descSelector of descSelectors) {
                                const descEl = element.querySelector(descSelector);
                                if (descEl && descEl.textContent.trim()) {
                                    listing.description = descEl.textContent.trim();
                                    break;
                                }
                            }
                            
                            // Extract URL
                            const linkEl = element.querySelector('a[href]');
                            if (linkEl) {
                                listing.url = linkEl.href;
                            }
                            
                            // Only include if it has essential information
                            if (listing.title && (listing.price || listing.description)) {
                                listings.push(listing);
                            }
                        }
                    }
                    
                    return listings;
                }
            """)
            
            # Process and validate listings
            valid_listings = []
            for listing in listings:
                if listing.get('title') and (listing.get('price') or listing.get('description')):
                    # Determine source from URL
                    source = get_source_from_url(url)
                    listing['source'] = source
                    valid_listings.append(listing)
            
            return valid_listings
            
        except Exception as e:
            print(f"Error extracting listings from page {url}: {e}")
            return []

async def search_google_playwright(params: Dict, enable_deep_search: bool = True, progress_callback=None) -> Dict:
    """Main function to search using Google Playwright scraper with deep search"""
    print("Starting Google Playwright search with deep search...")
    
    # Use the same approach as the working browser test
    print("You should see a Chrome browser window open!")
    
    async with GooglePlaywrightScraper(enable_deep_search=enable_deep_search) as scraper:
        print("Browser context manager entered. Starting search...")
        results = await scraper.search_with_multiple_queries(params, progress_callback=progress_callback)
        print(f"Search completed. Found {len(results)} results.")
        
        # Get deep search report if enabled
        if enable_deep_search and scraper.tracker:
            report = scraper.tracker.get_report()
            print(f"\nDEEP SEARCH REPORT:")
            print(f"Total links visited: {report['total_visited']}")
            print(f"Total links shortlisted: {report['total_shortlisted']}")
            print(f"Search depth: {report['search_depth']}")
            
            return {
                'listings': results,
                'deep_search_report': report
            }
        else:
            return {
                'listings': results,
                'deep_search_report': None
            } 