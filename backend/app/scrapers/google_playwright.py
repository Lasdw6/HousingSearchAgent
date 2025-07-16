import asyncio
import re
import logging
from typing import List, Dict, Optional, Set
from playwright.async_api import async_playwright, Browser, Page
from urllib.parse import urlparse, unquote
import random
import time
import screenenv
import os
from dotenv import load_dotenv
from smolagents import OpenAIServerModel, CodeAgent
import traceback

logger = logging.getLogger(__name__)

load_dotenv()

# Set up the LLM agent (once, at module level)
openai_api_key = os.getenv("OPENAI_API_KEY")
model = OpenAIServerModel(
    model_id="gpt-4o-mini",  # or "gpt-4o-mini" if that's your deployment name
    api_base="https://api.openai.com/v1",
    api_key=openai_api_key,
)
agent = CodeAgent(
    tools=[],  # No browser tools needed for this use case
    model=model,
    max_steps=3,
    verbosity_level=2,
)

# Action execution helpers (move outside try block)
async def execute_action_type(page, selector, text_val):
    print(f"[EXECUTE] Typing '{text_val}' into '{selector}'")
    el = await page.query_selector(selector)
    if el:
        is_visible = await el.is_visible()
        is_enabled = await el.is_enabled()
        if is_visible and is_enabled:
            await el.fill(text_val)
            await asyncio.sleep(1)
        else:
            print(f"Element {selector} is not visible or not enabled.")
            return False
    else:
        print(f"No input found for selector: {selector}")
        return False
    return True

async def execute_action_click(page, text_val=None, selector=None):
    if text_val:
        print(f"[EXECUTE] Clicking element with text: {text_val}")
        el = await page.query_selector(f'xpath=//*[text()[contains(., "{text_val}")]]')
    elif selector:
        print(f"[EXECUTE] Clicking element with selector: {selector}")
        el = await page.query_selector(selector)
    else:
        print("[EXECUTE] No valid click target specified.")
        return False
    if el:
        await el.click()
        await asyncio.sleep(2)
        return True
    else:
        print(f"No element found for click target: {text_val or selector}")
        return False

async def execute_action_submit(page, selector):
    print(f"[EXECUTE] Submitting form/input: {selector}")
    el = await page.query_selector(selector)
    if el:
        await el.press('Enter')
        await asyncio.sleep(2)
        return True
    else:
        print(f"No input found for selector: {selector}")
        return False

async def execute_action_follow(page, url_to_follow):
    print(f"[EXECUTE] Following link: {url_to_follow}")
    await page.goto(url_to_follow, wait_until='domcontentloaded', timeout=15000)
    await asyncio.sleep(2)
    return True

async def verify_listing_with_playwright(url, params):
    print(f"Visiting: {url}")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=15000)
            await asyncio.sleep(2)
            max_steps = 3
            for step in range(max_steps):
                # Get visible text (truncate to 4000 chars for LLM)
                text = await page.inner_text('body')
                text = text[:4000]
                # Get clickable elements (links, buttons, submit inputs)
                clickables = await page.evaluate("""
() => {
    const elements = Array.from(document.querySelectorAll('a, button, input[type=submit], input[type=button]'));
    return elements.map(el => ({
        tag: el.tagName,
        text: el.innerText || el.value || '',
        selector: el.getAttribute('id') ? ('#' + el.getAttribute('id')) : (el.getAttribute('class') ? (el.tagName.toLowerCase() + '.' + Array.from(el.classList).join('.')) : el.tagName.toLowerCase()),
        html: el.outerHTML.slice(0, 120)
    }));
}
""")
                # Get input fields
                inputs = await page.evaluate("""
() => {
    const elements = Array.from(document.querySelectorAll('input, textarea, select'));
    return elements.map(el => ({
        tag: el.tagName,
        name: el.name || '',
        placeholder: el.placeholder || '',
        selector: el.getAttribute('id') ? ('#' + el.getAttribute('id')) : (el.getAttribute('class') ? (el.tagName.toLowerCase() + '.' + Array.from(el.classList).join('.')) : el.tagName.toLowerCase()),
        html: el.outerHTML.slice(0, 120)
    }));
}
""")
                # Compose the LLM prompt
                prompt = f"""
You are a housing search navigation agent. The user is looking for a listing with these criteria:
{params}

Here is the text content of the web page:
{text}

Here are the clickable elements on the page (tag, text/value, selector, html snippet):
{clickables}

Here are the input fields on the page (tag, name, placeholder, selector, html snippet):
{inputs}

Your goal is to use the website as a real user would: fill out search fields, set filters, click search/apply buttons, and follow links as needed to reach the page with actual housing listings that match the user's criteria. You may need to:
- Type the location, price, or other details into the appropriate fields
- Click buttons to open search/filter panels or submit the search
- Follow links to results pages

At each step, output up to 3 actions as a JSON array of objects, in sequence, before the page changes. If you reach a page that shows actual listings matching the user's criteria, respond with a single JSON object with type 'LISTING' and the listing fields. If there are no more actions to try, respond with a single JSON object with type 'NO_MATCH'.

Each action object should have a 'type' field (one of: 'ACTION_CLICK', 'ACTION_TYPE', 'ACTION_SUBMIT', 'ACTION_FOLLOW', 'LISTING', 'NO_MATCH') and the relevant fields:
- For clicking: {"type": "ACTION_CLICK", "text": "..."} or {"type": "ACTION_CLICK", "selector": "..."}
- For typing: {"type": "ACTION_TYPE", "selector": "...", "text": "..."}
- For submitting: {"type": "ACTION_SUBMIT", "selector": "..."}
- For following a link: {"type": "ACTION_FOLLOW", "url": "..."}
- For a found listing: {"type": "LISTING", "title": ..., "price": ..., "address": ..., "description": ..., "url": ...}
- For no more actions: {"type": "NO_MATCH"}

IMPORTANT: Output ONLY the JSON array or object, with no markdown, code blocks, or explanations.
"""
                try:
                    result = agent.run(prompt)
                    print(f"Agent result (step {step+1}): {repr(result)}")
                    import json
                    # Try to parse the LLM output as JSON
                    result_clean = result.strip()
                    # Remove code block markers if present
                    if result_clean.startswith("```") or result_clean.startswith("```json"):
                        result_clean = result_clean.strip('`').replace('json', '').strip()
                    actions = json.loads(result_clean)
                    # If a single object is returned, wrap in a list for uniformity
                    if isinstance(actions, dict):
                        actions = [actions]
                except Exception as e:
                    print("Error during LLM agent run or JSON parsing:", repr(e))
                    traceback.print_exc()
                    break
                # Execute up to 3 actions per LLM response
                for action in actions[:3]:
                    action_type = action.get('type', '').upper()
                    if action_type == 'LISTING':
                        print("Returning listing:", repr(action))
                        return {"raw_agent_output": action, "url": url}
                    elif action_type == 'ACTION_TYPE':
                        selector = action.get('selector')
                        text_val = action.get('text')
                        if selector and text_val:
                            success = await execute_action_type(page, selector, text_val)
                            if not success:
                                break
                        else:
                            print("Malformed ACTION_TYPE action:", repr(action))
                            break
                    elif action_type == 'ACTION_CLICK':
                        text_val = action.get('text')
                        selector = action.get('selector')
                        if text_val:
                            success = await execute_action_click(page, text_val=text_val)
                            if not success:
                                break
                        elif selector:
                            success = await execute_action_click(page, selector=selector)
                            if not success:
                                break
                        else:
                            print("Malformed ACTION_CLICK action:", repr(action))
                            break
                    elif action_type == 'ACTION_SUBMIT':
                        selector = action.get('selector')
                        if selector:
                            success = await execute_action_submit(page, selector)
                            if not success:
                                break
                        else:
                            print("Malformed ACTION_SUBMIT action:", repr(action))
                            break
                    elif action_type == 'ACTION_FOLLOW':
                        url_to_follow = action.get('url')
                        if url_to_follow:
                            await execute_action_follow(page, url_to_follow)
                        else:
                            print("Malformed ACTION_FOLLOW action:", repr(action))
                            break
                    elif action_type == 'NO_MATCH':
                        print("No match found for this page.")
                        break
                    else:
                        print("Malformed or unhandled action:", repr(action))
                        continue
        except Exception as e:
            print("Failed to visit", url, ":", e)
        finally:
            await browser.close()
        return None

# Replace the old verify_listing with the new one
verify_listing = verify_listing_with_playwright

class GooglePlaywrightScraper:
    """Advanced Google search scraper using Playwright"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.visited_urls: Set[str] = set()
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
        self.playwright = await async_playwright().start()
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
        self.page = await self.browser.new_page()
        await self.page.set_extra_http_headers({
            'User-Agent': random.choice(self.user_agents)
        })
    
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
                
                await self.page.goto(search_url, wait_until='networkidle')
                await asyncio.sleep(random.uniform(2, 4))  # Random delay
                
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
            await self.page.wait_for_selector('div#search, div#rso', timeout=10000)
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
    
    async def search_duckduckgo(self, query: str, max_pages: int = 3) -> List[Dict]:
        """Search DuckDuckGo and extract results from multiple pages"""
        results = []
        try:
            for page_num in range(max_pages):
                search_url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
                if page_num > 0:
                    search_url += f"&s={page_num * 30}"
                logger.info(f"Searching DuckDuckGo page {page_num + 1} for: {query}")
                await self.page.goto(search_url, wait_until='networkidle')
                await asyncio.sleep(random.uniform(2, 4))
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

    async def search_with_multiple_queries(self, params: Dict, max_queries: int = 3) -> List[Dict]:
        all_results = []
        queries_to_try = self.search_queries[:max_queries]
        for i, query in enumerate(queries_to_try):
            logger.info(f"Trying search query {i + 1}: {query}")
            # Try DuckDuckGo first
            try:
                search_results = await self.search_duckduckgo(query, max_pages=3)
            except Exception as e:
                logger.warning(f"DuckDuckGo search failed, falling back to Google: {e}")
                search_results = []
            # If DuckDuckGo fails or returns no results, try Google
            if not search_results:
                logger.info("Trying Google fallback...")
                try:
                    search_results = await self.search_google(query, max_pages=3)
                except Exception as e:
                    logger.warning(f"Google search also failed: {e}")
                    search_results = []
            # Verify each result (limit to first 5 links)
            for result in search_results[:5]:
                if len(all_results) >= 50:
                    break
                verified_listing = await verify_listing(result['url'], params)
                if verified_listing:
                    all_results.append(verified_listing)
            if i < len(queries_to_try) - 1:
                await asyncio.sleep(random.uniform(3, 6))
        return all_results

async def search_google_playwright(params: Dict) -> List[Dict]:
    """Main function to search using Google Playwright scraper"""
    async with GooglePlaywrightScraper() as scraper:
        return await scraper.search_with_multiple_queries(params) 