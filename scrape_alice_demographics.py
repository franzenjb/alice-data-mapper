#!/usr/bin/env python3
"""
Scrape ALICE demographic data from Tableau Public visualizations
"""

import json
import requests
import re
from urllib.parse import urlencode

print("Scraping ALICE demographic data from Tableau visualizations...")

# Tableau Public API endpoints from the embedded visualizations
tableau_vizzes = [
    {
        'name': 'National_Comparison_2023',
        'url': 'https://public.tableau.com/views/State_bars_2023/WebDash',
        'sheet': 'WebDash'
    },
    {
        'name': 'National_Demographics_2023', 
        'url': 'https://public.tableau.com/views/National_Demographics_2023/Dashboard1',
        'sheet': 'Dashboard1'
    }
]

def get_tableau_data(viz_url):
    """Extract data from Tableau Public visualization"""
    try:
        # Extract the viz ID from the URL
        match = re.search(r'/views/([^/]+)/([^?]+)', viz_url)
        if not match:
            return None
            
        viz_id = match.group(1)
        sheet = match.group(2)
        
        # Tableau Public data export URL pattern
        base_url = 'https://public.tableau.com'
        
        # Try to get the viz metadata first
        session_url = f"{base_url}/views/{viz_id}/{sheet}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        
        print(f"  Fetching: {session_url}")
        response = requests.get(session_url, headers=headers)
        
        if response.status_code == 200:
            # Look for the tableau data in the response
            # Tableau embeds initial data in the HTML
            text = response.text
            
            # Extract sessionid and other params
            sessionid_match = re.search(r'"sessionid":"([^"]+)"', text)
            if sessionid_match:
                sessionid = sessionid_match.group(1)
                print(f"    Found session: {sessionid[:20]}...")
                
            # Try to find the data export endpoints
            # Tableau allows CSV export through specific endpoints
            export_patterns = [
                r'exportcrosstab[^"]*',
                r'exportData[^"]*', 
                r'vudcsv[^"]*'
            ]
            
            for pattern in export_patterns:
                matches = re.findall(pattern, text)
                if matches:
                    print(f"    Found export endpoints: {len(matches)}")
                    
            return {'viz_id': viz_id, 'sheet': sheet, 'html_size': len(text)}
        else:
            print(f"    Error: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"    Error: {e}")
        return None

# Process each Tableau viz
results = {}
for viz in tableau_vizzes:
    print(f"\nProcessing {viz['name']}...")
    data = get_tableau_data(viz['url'])
    if data:
        results[viz['name']] = data

print("\n" + "="*50)
print("Summary of Tableau data sources found:")
print("="*50)
for name, data in results.items():
    print(f"\n{name}:")
    print(f"  Viz ID: {data.get('viz_id', 'N/A')}")
    print(f"  Sheet: {data.get('sheet', 'N/A')}")
    print(f"  HTML Size: {data.get('html_size', 0):,} bytes")

# Now let's try the ALICE API endpoints directly
print("\n" + "="*50)
print("Testing ALICE API endpoints...")
print("="*50)

api_base = "https://www.unitedforalice.org/api"
api_endpoints = [
    "/State/partner-states-us",
    "/geo-json-united-states",
    "/geo-json-state?stateFP=01",  # Alabama as test
    "/county-data",
    "/demographics",
    "/household-types",
    "/age-groups"
]

api_results = {}
for endpoint in api_endpoints:
    url = api_base + endpoint
    print(f"\nTesting: {url}")
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json() if 'json' in response.headers.get('content-type', '') else response.text
            if isinstance(data, list):
                print(f"  ✓ Success: {len(data)} records")
                api_results[endpoint] = data[:5]  # Save sample
            elif isinstance(data, dict):
                print(f"  ✓ Success: {len(data)} keys")
                api_results[endpoint] = data
            else:
                print(f"  ✓ Success: {len(str(data))} bytes")
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

# Save discovered data
with open('alice_api_endpoints.json', 'w') as f:
    json.dump({
        'tableau_sources': results,
        'api_endpoints': api_results,
        'notes': {
            'tableau_urls': [v['url'] for v in tableau_vizzes],
            'discovered': 'Tableau Public visualizations contain demographic breakdowns',
            'demographics': ['Age', 'Household Type', 'Race/Ethnicity', 'Rural/Urban']
        }
    }, f, indent=2)

print("\n✅ Saved findings to alice_api_endpoints.json")

# Additional discovery - check for downloadable reports
print("\n" + "="*50)
print("Checking for downloadable data files...")
print("="*50)

report_urls = [
    "https://www.unitedforalice.org/Attachments/AllReports/2023_ALICE_Report_National.xlsx",
    "https://www.unitedforalice.org/Attachments/AllReports/2023_ALICE_Data_National.csv",
    "https://www.unitedforalice.org/national-data.json",
    "https://alice.uwmnj.org/api/data/export",
    "https://www.unitedforalice.org/Attachments/AllReports/state-of-alice-report-united-states-2025.pdf"
]

for url in report_urls:
    print(f"\nChecking: {url}")
    try:
        response = requests.head(url, timeout=5, allow_redirects=True)
        if response.status_code == 200:
            size = response.headers.get('content-length', 'unknown')
            print(f"  ✓ Available: {size} bytes")
        else:
            print(f"  ✗ Status: {response.status_code}")
    except Exception as e:
        print(f"  ✗ Error: {e}")

print("\n📊 Note: Tableau visualizations contain the demographic data we need.")
print("To extract full data, we need to either:")
print("1. Use Tableau's export functionality (requires browser automation)")
print("2. Contact United for ALICE for direct data access")
print("3. Parse the embedded data from Tableau visualization HTML")