#!/usr/bin/env python3
"""Fix more indentation issues in google_playwright.py"""

with open('app/scrapers/google_playwright.py', 'r') as f:
    lines = f.readlines()

# Check current state around line 1261
for i in range(1258, 1268):
    if i < len(lines):
        print(f'Line {i+1}: {repr(lines[i])}')

print('\nFixing indentation...')

# Fix the break statement indentation around line 1261
lines[1260] = '                        break\n'  # Line 1261

with open('app/scrapers/google_playwright.py', 'w') as f:
    f.writelines(lines)

print('Fixed break statement indentation')

