#!/usr/bin/env python3
"""
Enhanced ALICE Demographic Scraper
Extracts detailed demographic data by intercepting Tableau data requests
"""

import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright
import re
from datetime import datetime
import os

class EnhancedDemographicScraper:
    def __init__(self):
        self.tableau_url = "https://public.tableau.com/views/UnitedForALICE-Maps/Story"
        self.collected_data = []
        self.network_responses = []
        
    async def intercept_network_data(self, response):
        """Intercept and save network responses containing data"""
        try:
            url = response.url
            
            # Look for Tableau data endpoints
            if any(keyword in url.lower() for keyword in ['data', 'bootstrapSession', 'vizql', 'sessions']):
                if response.status == 200:
                    content_type = response.headers.get('content-type', '')
                    
                    if 'json' in content_type:
                        try:
                            data = await response.json()
                            self.network_responses.append({
                                'url': url[:100],
                                'timestamp': datetime.now().isoformat(),
                                'data': data
                            })
                            print(f"  📦 Captured JSON data from: {url[:50]}...")
                        except:
                            pass
                            
                    elif 'text' in content_type or 'html' in content_type:
                        try:
                            text = await response.text()
                            # Look for embedded JSON in HTML/text responses
                            self.extract_embedded_json(text, url)
                        except:
                            pass
        except Exception as e:
            pass
            
    def extract_embedded_json(self, text, source_url):
        """Extract JSON data embedded in HTML/JavaScript"""
        # Patterns that might contain data
        patterns = [
            r'bootstrapSession\s*=\s*({.+?});',
            r'initialDataModel\s*=\s*({.+?});',
            r'model\s*=\s*({.+?});',
            r'"data":\s*(\[.+?\])',
            r'"values":\s*(\[.+?\])',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    data = json.loads(match)
                    if data and (isinstance(data, dict) or isinstance(data, list)):
                        self.collected_data.append({
                            'source': source_url[:50],
                            'pattern': pattern[:20],
                            'data': data
                        })
                        print(f"  ✅ Extracted data using pattern: {pattern[:30]}...")
                except:
                    pass
                    
    async def scrape_with_interactions(self):
        """Main scraping function with user interactions"""
        print("🚀 Starting Enhanced Demographic Scraper")
        print("📊 Target: Tableau Public ALICE Maps")
        print("-" * 60)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Keep visible to see what's happening
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = await context.new_page()
            
            # Set up network interception
            page.on("response", self.intercept_network_data)
            
            print("📍 Navigating to Tableau visualization...")
            await page.goto(self.tableau_url, wait_until='networkidle', timeout=60000)
            
            print("⏳ Waiting for Tableau to load...")
            await asyncio.sleep(5)
            
            # Try to interact with the visualization
            await self.interact_with_tableau(page)
            
            # Give time for all network requests to complete
            await asyncio.sleep(3)
            
            await browser.close()
            
        # Process and save collected data
        self.process_collected_data()
        
    async def interact_with_tableau(self, page):
        """Interact with Tableau viz to trigger data loads"""
        print("🖱️ Interacting with visualization...")
        
        # Common Tableau selectors
        selectors_to_try = [
            # Dropdown menus
            '[class*="dropdown"]',
            '[class*="select"]',
            '[class*="filter"]',
            
            # Tab buttons
            '[class*="tab"]',
            '[role="tab"]',
            
            # Parameter controls
            '[class*="parameter"]',
            '[class*="control"]',
            
            # Tableau specific
            '.tab-zone',
            '.tab-text-name',
            '.tabComboBoxButton',
            '.FIItem',
            
            # Text that might be clickable
            'text="Demographics"',
            'text="Age"',
            'text="Household"',
            'text="Race"'
        ]
        
        for selector in selectors_to_try:
            try:
                elements = await page.locator(selector).all()
                if elements:
                    print(f"  🎯 Found {len(elements)} elements matching: {selector}")
                    
                    # Click first element
                    if len(elements) > 0:
                        await elements[0].click()
                        await asyncio.sleep(2)
            except:
                pass
                
        # Try scrolling to trigger lazy loading
        await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
        await asyncio.sleep(2)
        
    def process_collected_data(self):
        """Process and structure collected data"""
        print(f"\n📊 Processing {len(self.collected_data)} data chunks...")
        print(f"📡 Captured {len(self.network_responses)} network responses")
        
        # Extract demographic information
        demographics = {
            'age_data': [],
            'household_data': [],
            'race_data': [],
            'county_data': []
        }
        
        # Process collected data
        for item in self.collected_data:
            data = item['data']
            
            # Look for demographic indicators in the data
            if isinstance(data, dict):
                self.extract_demographics_from_dict(data, demographics)
            elif isinstance(data, list):
                for d in data:
                    if isinstance(d, dict):
                        self.extract_demographics_from_dict(d, demographics)
                        
        # Save results
        self.save_results(demographics)
        
    def extract_demographics_from_dict(self, data, demographics):
        """Extract demographic information from dictionary"""
        # Convert to string to search for keywords
        data_str = str(data).lower()
        
        # Check for demographic categories
        if 'age' in data_str or 'years' in data_str:
            demographics['age_data'].append(data)
            
        if 'household' in data_str or 'married' in data_str or 'single' in data_str:
            demographics['household_data'].append(data)
            
        if 'race' in data_str or 'hispanic' in data_str or 'black' in data_str or 'white' in data_str:
            demographics['race_data'].append(data)
            
        if 'county' in data_str or 'fips' in data_str:
            demographics['county_data'].append(data)
            
    def save_results(self, demographics):
        """Save scraped demographics to files"""
        # Save raw data
        with open('alice_demographics_scraped.json', 'w') as f:
            json.dump({
                'scraped_at': datetime.now().isoformat(),
                'demographics': demographics,
                'network_responses': self.network_responses[:10]  # Save sample
            }, f, indent=2, default=str)
            
        # Create summary
        summary = {
            'timestamp': datetime.now().isoformat(),
            'data_collected': {
                'age_records': len(demographics['age_data']),
                'household_records': len(demographics['household_data']),
                'race_records': len(demographics['race_data']),
                'county_records': len(demographics['county_data'])
            },
            'network_responses': len(self.network_responses)
        }
        
        with open('scraping_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
            
        print("\n✅ Data saved to:")
        print("  📁 alice_demographics_scraped.json")
        print("  📁 scraping_summary.json")
        
        print(f"\n📊 Summary:")
        for key, value in summary['data_collected'].items():
            print(f"  • {key}: {value}")

async def main():
    scraper = EnhancedDemographicScraper()
    await scraper.scrape_with_interactions()

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════╗
    ║   ENHANCED ALICE DEMOGRAPHIC SCRAPER        ║
    ║   Extracting detailed demographic data      ║
    ╚══════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())