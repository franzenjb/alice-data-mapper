#!/usr/bin/env python3
"""
ALICE API Explorer
Discovers and extracts data from ALICE website API endpoints
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

class ALICEAPIExplorer:
    def __init__(self):
        self.base_url = "https://unitedforalice.org"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Referer': 'https://unitedforalice.org/all-maps'
        })
        
        self.discovered_endpoints = []
        self.demographic_data = {}
        
    def explore_endpoints(self):
        """Discover API endpoints"""
        print("🔍 Exploring ALICE API endpoints...")
        
        # Known and potential endpoints
        endpoints_to_try = [
            "/api/State/partner-states-us",
            "/api/geo-json-united-states", 
            "/api/geo-json-state",
            "/api/data/demographics",
            "/api/data/age-groups",
            "/api/data/household-types",
            "/api/data/race-ethnicity",
            "/api/tableau/data",
            "/api/maps/data",
            "/api/state/{state_code}/demographics",
            "/api/county/data",
            "/api/statistics/alice",
            "/National/Index",
            "/State/Index"
        ]
        
        for endpoint in endpoints_to_try:
            full_url = self.base_url + endpoint
            
            # Try with different state codes
            if "{state_code}" in endpoint:
                for state_code in ["12", "13", "48"]:  # FL, GA, TX
                    test_url = full_url.replace("{state_code}", state_code)
                    self.test_endpoint(test_url)
            else:
                self.test_endpoint(full_url)
                
    def test_endpoint(self, url):
        """Test if an endpoint returns data"""
        try:
            response = self.session.get(url, timeout=5)
            if response.status_code == 200:
                content_type = response.headers.get('Content-Type', '')
                
                if 'json' in content_type:
                    data = response.json()
                    print(f"✅ Found JSON endpoint: {url}")
                    print(f"   Data preview: {str(data)[:200]}...")
                    self.discovered_endpoints.append({
                        'url': url,
                        'type': 'json',
                        'sample': data[:3] if isinstance(data, list) else data
                    })
                    
                elif 'html' in content_type and 'tableau' in response.text.lower():
                    print(f"📊 Found Tableau page: {url}")
                    self.extract_tableau_config(response.text, url)
                    
        except Exception as e:
            pass
            
    def extract_tableau_config(self, html_content, url):
        """Extract Tableau configuration from HTML"""
        import re
        
        # Look for Tableau viz configuration
        patterns = [
            r'tableauViz\s*=\s*({[^}]+})',
            r'vizql/w/([^/]+)/v/([^"]+)',
            r'tableau\.vizql\.dll/([^"]+)',
            r'host_url["\']:\s*["\'](https?://[^"\']+)',
            r'site_root["\']:\s*["\'](/[^"\']*)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content)
            if matches:
                print(f"   📈 Found Tableau config: {matches[0][:100]}...")
                
    def fetch_demographic_data(self):
        """Attempt to fetch demographic data using discovered endpoints"""
        print("\n📊 Fetching demographic data...")
        
        # Try the interactive map page with different parameters
        map_url = "https://public.tableau.com/views/UnitedForALICE-Maps/Story"
        
        # Parameters that Tableau might accept
        params = {
            ':embed': 'y',
            ':showVizHome': 'no',
            ':display_count': 'yes',
            ':showTabs': 'y',
            'Demographics': 'Age'
        }
        
        try:
            response = self.session.get(map_url, params=params)
            if response.status_code == 200:
                print(f"✅ Accessed Tableau public viz")
                # Parse response for data
                self.parse_tableau_response(response.text)
        except:
            pass
            
    def parse_tableau_response(self, content):
        """Parse Tableau response for data"""
        import re
        
        # Look for JSON data embedded in the response
        json_pattern = r'bootstrapData["\']?\s*[:=]\s*({.+?})\s*[,;]'
        matches = re.findall(json_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                data = json.loads(match)
                if data:
                    print(f"   📦 Found embedded data: {list(data.keys())}")
            except:
                pass
                
    def search_census_alternative(self):
        """Search Census Bureau API as alternative"""
        print("\n🏛️ Checking Census Bureau API (ALICE's data source)...")
        
        census_base = "https://api.census.gov/data"
        
        # American Community Survey endpoints
        acs_endpoints = [
            "/2022/acs/acs5",  # 5-year estimates
            "/2022/acs/acs1",  # 1-year estimates
        ]
        
        # Variables of interest for ALICE calculations
        variables = [
            "B17001_001E",  # Poverty status population
            "B11001_001E",  # Household types
            "B01001_001E",  # Age and sex
            "B03002_001E",  # Hispanic origin by race
            "B19013_001E",  # Median household income
        ]
        
        for endpoint in acs_endpoints[:1]:
            url = f"{census_base}{endpoint}"
            params = {
                "get": ",".join(variables[:3]),
                "for": "county:*",
                "in": "state:12",  # Florida
                "key": "YOUR_CENSUS_API_KEY"  # Would need free key from census.gov
            }
            
            print(f"   📊 Census endpoint: {url}")
            print(f"   📝 Would retrieve: Age, Household, Poverty data")
            print(f"   🔑 Note: Requires free API key from census.gov/developers")
            
    def save_discoveries(self):
        """Save discovered endpoints and data"""
        output = {
            "discovered": datetime.now().isoformat(),
            "endpoints": self.discovered_endpoints,
            "demographic_data": self.demographic_data
        }
        
        with open('alice_api_discoveries.json', 'w') as f:
            json.dump(output, f, indent=2)
            
        print(f"\n💾 Saved discoveries to alice_api_discoveries.json")
        print(f"📊 Found {len(self.discovered_endpoints)} working endpoints")

def main():
    print("""
    ╔════════════════════════════════════════════╗
    ║   ALICE API EXPLORER                      ║
    ║   Discovering data endpoints              ║
    ╚════════════════════════════════════════════╝
    """)
    
    explorer = ALICEAPIExplorer()
    
    # Explore endpoints
    explorer.explore_endpoints()
    
    # Try to fetch demographic data
    explorer.fetch_demographic_data()
    
    # Check Census Bureau as alternative
    explorer.search_census_alternative()
    
    # Save findings
    explorer.save_discoveries()
    
    print("\n✅ Exploration complete!")
    
    # Provide recommendations
    print("""
    📋 RECOMMENDATIONS:
    
    1. The ALICE site uses Tableau Public visualizations
       → Data is embedded but not easily extractable
    
    2. Census Bureau API is the best alternative:
       → Same source data ALICE uses
       → Free API key at census.gov/developers
       → Full demographic breakdowns available
    
    3. For immediate needs:
       → We already have county-level data
       → Can enhance with Census API for demographics
    """)

if __name__ == "__main__":
    main()