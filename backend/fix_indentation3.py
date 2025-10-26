#!/usr/bin/env python3
"""Fix remaining indentation issues in google_playwright.py"""

with open('app/scrapers/google_playwright.py', 'r') as f:
    lines = f.readlines()

# Check current state around line 1267
for i in range(1258, 1270):
    if i < len(lines):
        print(f'Line {i+1}: {repr(lines[i])}')

print('\nFixing indentation...')

# Fix the for loop indentation around lines 1259-1267
lines[1258] = '                for result in search_results[:3]:\n'  # Line 1259
lines[1259] = '                    if len(all_results) >= 30:  # Reduced from 50 to 30\n'  # Line 1260
lines[1260] = '                        break\n'  # Line 1261
lines[1261] = '                    \n'  # Line 1262
lines[1262] = '                    if self.enable_deep_search and self.tracker:\n'  # Line 1263
lines[1263] = '                        task = self.deep_search_listing_concurrent(result[\'url\'], params, progress_callback)\n'  # Line 1264
lines[1264] = '                    else:\n'  # Line 1265
lines[1265] = '                        task = self.verify_listing_concurrent(result[\'url\'], params, progress_callback)\n'  # Line 1266
lines[1266] = '                    tasks.append(task)\n'  # Line 1267

with open('app/scrapers/google_playwright.py', 'w') as f:
    f.writelines(lines)

print('Fixed for loop indentation')

