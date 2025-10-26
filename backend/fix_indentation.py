#!/usr/bin/env python3
"""Fix indentation issues in google_playwright.py"""

with open('app/scrapers/google_playwright.py', 'r') as f:
    lines = f.readlines()

# Check current state around line 504
for i in range(500, 510):
    if i < len(lines):
        print(f'Line {i+1}: {repr(lines[i])}')

print('\nFixing indentation...')

# Fix the except block indentation around line 504
lines[503] = '    except Exception as e:\n'  # Line 504
lines[504] = '        print(f"Failed to extract data from {url}: {e}")\n'  # Line 505
lines[505] = '        return None\n'  # Line 506

with open('app/scrapers/google_playwright.py', 'w') as f:
    f.writelines(lines)

print('Fixed except block indentation')

