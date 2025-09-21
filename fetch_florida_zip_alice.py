#!/usr/bin/env python3
"""
Fetch ALICE data at ZIP code level for Florida
This script fetches granular ALICE data from United for ALICE website
"""

import requests
import json
import pandas as pd
from datetime import datetime

def fetch_florida_alice_zip_data():
    """
    Fetch ALICE data for Florida at ZIP code level
    """
    
    # Base URL for ALICE data
    base_url = "https://www.unitedforalice.org"
    
    # Headers to mimic browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.unitedforalice.org/county-reports/florida'
    }
    
    print("Fetching Florida ALICE data at ZIP code level...")
    
    # Try to find the data endpoint
    # This might need adjustment based on actual API structure
    endpoints_to_try = [
        "/api/florida/zip-codes",
        "/data/florida/zip",
        "/county-reports/florida/data/zip",
        "/api/data/florida?geography=zip",
        "/api/v1/state/florida/geography/zip"
    ]
    
    data = None
    for endpoint in endpoints_to_try:
        try:
            url = base_url + endpoint
            print(f"Trying: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"Success! Found data at: {url}")
                break
        except Exception as e:
            print(f"Failed: {e}")
            continue
    
    if not data:
        print("\nCouldn't find the API endpoint automatically.")
        print("Let me try to fetch the Excel file directly...")
        
        # Try Excel download links that might exist
        excel_urls = [
            "https://www.unitedforalice.org/downloads/florida-zip-codes.xlsx",
            "https://www.unitedforalice.org/data/florida/zip-codes.xlsx",
            "https://www.unitedforalice.org/county-reports/florida/download/zip-codes"
        ]
        
        for url in excel_urls:
            try:
                print(f"Trying Excel download: {url}")
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    # Save the Excel file
                    filename = f"florida_alice_zip_{datetime.now().strftime('%Y%m%d')}.xlsx"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Downloaded Excel file: {filename}")
                    
                    # Read the Excel file
                    df = pd.read_excel(filename)
                    print(f"Loaded {len(df)} ZIP codes")
                    print("\nColumns found:")
                    print(df.columns.tolist())
                    print("\nFirst few rows:")
                    print(df.head())
                    return df
            except Exception as e:
                print(f"Failed: {e}")
                continue
    
    return data

def create_zip_geojson(alice_data):
    """
    Create GeoJSON file for ZIP codes with ALICE data
    Note: This requires ZIP code boundary data which needs to be fetched separately
    """
    print("\nTo create GeoJSON, we need ZIP code boundaries...")
    print("You can get Florida ZIP code boundaries from:")
    print("1. Census TIGER/Line files: https://www.census.gov/geographies/mapping-files/time-series/geo/tiger-line-file.html")
    print("2. Select 2023 -> Web Interface -> ZIP Code Tabulation Areas")
    print("3. Filter for Florida")
    
    # Structure for combining with boundaries later
    output = {
        "type": "FeatureCollection",
        "name": "Florida_ALICE_ZIP_Codes",
        "features": []
    }
    
    if isinstance(alice_data, pd.DataFrame):
        # Convert DataFrame to dict for easier processing
        alice_dict = alice_data.to_dict('records')
        
        print(f"\nPrepared {len(alice_dict)} ZIP codes for GeoJSON conversion")
        print("Next step: Merge with ZIP code boundaries from Census TIGER files")
        
        # Save the data structure
        with open('florida_alice_zip_data.json', 'w') as f:
            json.dump(alice_dict, f, indent=2)
        print("Saved ALICE data to florida_alice_zip_data.json")
    
    return output

if __name__ == "__main__":
    # Fetch the data
    data = fetch_florida_alice_zip_data()
    
    if data:
        print("\n" + "="*50)
        print("DATA SUCCESSFULLY FETCHED!")
        print("="*50)
        
        # Try to create GeoJSON structure
        geojson = create_zip_geojson(data)
        
        print("\n" + "="*50)
        print("NEXT STEPS:")
        print("="*50)
        print("1. Download ZIP code boundaries from Census TIGER")
        print("2. Merge ALICE data with ZIP boundaries")
        print("3. Create complete GeoJSON for ArcGIS")
        print("4. Import into ArcGIS as a feature layer")
    else:
        print("\n" + "="*50)
        print("MANUAL STEPS REQUIRED:")
        print("="*50)
        print("1. Go to: https://www.unitedforalice.org/county-reports/florida")
        print("2. Select 'ZIP Codes' in the Sub-County Geographies section")
        print("3. Click on 'Download Excel' button")
        print("4. Save the file and run this script again with the file path")