#!/usr/bin/env python3
"""Fix all indentation issues in google_playwright.py"""

with open('app/scrapers/google_playwright.py', 'r') as f:
    lines = f.readlines()

# Fix the except block indentation around line 504
lines[503] = '    except Exception as e:\n'  # Line 504
lines[504] = '        print(f"Failed to extract data from {url}: {e}")\n'  # Line 505
lines[505] = '        return None\n'  # Line 506

# Fix the break statement indentation around line 1261
lines[1260] = '                        break\n'  # Line 1261

# Fix the for loop indentation around lines 1259-1267
lines[1258] = '                for result in search_results[:5]:\n'  # Line 1259
lines[1259] = '                    if len(all_results) >= 50:  # Increased back to 50\n'  # Line 1260
lines[1260] = '                        break\n'  # Line 1261
lines[1261] = '                    \n'  # Line 1262
lines[1262] = '                    if self.enable_deep_search and self.tracker:\n'  # Line 1263
lines[1263] = '                        task = self.deep_search_listing_concurrent(result[\'url\'], params, progress_callback)\n'  # Line 1264
lines[1264] = '                    else:\n'  # Line 1265
lines[1265] = '                        task = self.verify_listing_concurrent(result[\'url\'], params, progress_callback)\n'  # Line 1266
lines[1266] = '                    tasks.append(task)\n'  # Line 1267

with open('app/scrapers/google_playwright.py', 'w') as f:
    f.writelines(lines)

print('Fixed all indentation issues')

