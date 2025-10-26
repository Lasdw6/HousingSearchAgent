#!/usr/bin/env python3
"""
Standalone script to run the search functionality.
This avoids the Windows subprocess issues by running the search in a separate process.
"""

import asyncio
import json
import sys
import os
import argparse

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

async def run_search(params_file):
    """Run the search with the given parameters file"""
    import sys
    from app.scrapers.google_playwright import search_google_playwright
    
    with open(params_file, "r") as f:
        params = json.load(f)
    
    # Redirect stdout to stderr so only JSON goes to stdout
    import io
    from contextlib import redirect_stdout
    
    # Capture all print statements and send them to stderr
    with redirect_stdout(io.StringIO()) as captured:
        result = await search_google_playwright(params, enable_deep_search=True)
    
    # Print the captured output to stderr
    captured_output = captured.getvalue()
    if captured_output:
        print(captured_output, file=sys.stderr)
    
    # Only print JSON to stdout
    print(json.dumps(result))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run housing search")
    parser.add_argument("params_file", help="JSON file containing search parameters")
    args = parser.parse_args()
    
    asyncio.run(run_search(args.params_file))
