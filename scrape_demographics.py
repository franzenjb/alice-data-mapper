#!/usr/bin/env python3
"""
ALICE Demographic Data Scraper
Extracts detailed demographic breakdowns from United Way ALICE website
"""

import asyncio
import json
import pandas as pd
from playwright.async_api import async_playwright
import time
from datetime import datetime

class ALICEDemographicScraper:
    def __init__(self):
        self.base_url = "https://unitedforalice.org/all-maps"
        self.states = [
            "Alabama", "Arkansas", "Colorado", "Connecticut", "Delaware", 
            "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", 
            "Iowa", "Kansas", "Louisiana", "Maine", "Maryland", "Michigan", 
            "Minnesota", "Mississippi", "New Jersey", "New Mexico", "New York", 
            "North Carolina", "Ohio", "Oregon", "Pennsylvania", "South Carolina", 
            "Tennessee", "Texas", "Virginia", "Washington", "West Virginia"
        ]
        
        self.demographics = {
            "age_groups": [
                "Under 25 Years",
                "25 to 44 Years", 
                "45 to 64 Years",
                "Over 65 Years"
            ],
            "household_types": [
                "Married With Children",
                "Single Female With Children",
                "Single Male With Children", 
                "Single or Cohabitating Under 65"
            ],
            "race_ethnicity": [
                "Black",
                "White",
                "Hispanic",
                "Asian",
                "Hawaiian",
                "Two or More Races",
                "AI/AN"
            ]
        }
        
        self.results = []

    async def scrape_state_demographics(self, page, state):
        """Scrape demographic data for a single state"""
        print(f"\n📍 Scraping {state}...")
        
        try:
            # Navigate to the maps page
            await page.goto(self.base_url, wait_until="networkidle")
            await asyncio.sleep(3)
            
            # Wait for and interact with Tableau viz
            # Look for the Tableau iframe or embedded viz
            tableau_frame = await page.wait_for_selector('iframe[title*="Data Visualization"], .tableauPlaceholder', timeout=10000)
            
            if tableau_frame:
                print(f"  ✓ Found Tableau visualization for {state}")
                
                # Try to extract data from Tableau
                # This varies based on how Tableau is embedded
                await self.extract_tableau_data(page, state)
            
        except Exception as e:
            print(f"  ✗ Error scraping {state}: {str(e)}")
            
    async def extract_tableau_data(self, page, state):
        """Extract data from Tableau visualization"""
        
        # Method 1: Try to intercept network requests
        data_found = False
        
        def handle_response(response):
            if 'tableau' in response.url or 'data' in response.url:
                print(f"  → Intercepted data request: {response.url[:100]}...")
        
        page.on("response", handle_response)
        
        # Try clicking through different demographic filters
        for category, options in self.demographics.items():
            print(f"  📊 Checking {category}...")
            
            for option in options:
                try:
                    # Look for filter dropdowns or buttons
                    filter_selector = f'text="{option}"'
                    if await page.locator(filter_selector).count() > 0:
                        await page.click(filter_selector)
                        await asyncio.sleep(2)
                        
                        # Try to extract visible data
                        data = await self.extract_visible_data(page, state, category, option)
                        if data:
                            self.results.append(data)
                            data_found = True
                            
                except Exception as e:
                    continue
        
        if not data_found:
            print(f"  ⚠️  Could not extract detailed data for {state}")
            
    async def extract_visible_data(self, page, state, category, demographic):
        """Extract visible data from the page"""
        try:
            # Look for data in various formats
            data_selectors = [
                '.tableau-tooltip',
                '[class*="tooltip"]',
                '[class*="data"]',
                'text=/\\d+\\.\\d+%/',  # Percentage values
                'text=/\\d{1,3},\\d{3}/'  # Formatted numbers
            ]
            
            for selector in data_selectors:
                elements = await page.locator(selector).all()
                if elements:
                    values = []
                    for el in elements[:5]:  # Get first 5 values
                        text = await el.text_content()
                        if text:
                            values.append(text.strip())
                    
                    if values:
                        return {
                            "state": state,
                            "category": category,
                            "demographic": demographic,
                            "values": values,
                            "timestamp": datetime.now().isoformat()
                        }
        except:
            pass
        return None

    async def run_scraper(self):
        """Main scraper execution"""
        print("🚀 Starting ALICE Demographic Data Scraper")
        print(f"📋 Target: {len(self.states)} states")
        print(f"📊 Demographics: Age, Household Type, Race/Ethnicity")
        print("-" * 50)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=False,  # Set to True for production
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            
            page = await context.new_page()
            
            # Scrape each state
            for state in self.states[:3]:  # Start with first 3 states for testing
                await self.scrape_state_demographics(page, state)
                await asyncio.sleep(2)  # Be respectful with requests
            
            await browser.close()
        
        # Save results
        self.save_results()
        
    def save_results(self):
        """Save scraped data to JSON and CSV"""
        if self.results:
            # Save to JSON
            with open('alice_demographics_raw.json', 'w') as f:
                json.dump(self.results, f, indent=2)
            
            print(f"\n✅ Saved {len(self.results)} demographic records")
            print("📁 Output: alice_demographics_raw.json")
        else:
            print("\n⚠️  No demographic data was extracted")

async def main():
    scraper = ALICEDemographicScraper()
    await scraper.run_scraper()

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   ALICE DEMOGRAPHIC DATA SCRAPER          ║
    ║   Extracting age, household, race data    ║
    ╔════════════════════════════════════════════╝
    """)
    
    asyncio.run(main())