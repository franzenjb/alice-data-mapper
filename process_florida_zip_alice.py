#!/usr/bin/env python3
"""
Process Florida ALICE ZIP code data and create ArcGIS-ready GeoJSON
This script processes downloaded ALICE ZIP data and merges with Census boundaries
"""

import pandas as pd
import json
import requests
import zipfile
import os
from pathlib import Path

def download_census_zip_boundaries(state_fips="12"):
    """
    Download ZIP code boundaries from Census TIGER files
    Florida FIPS code is 12
    """
    print("Downloading Census ZIP code boundaries for Florida...")
    
    # Census TIGER file URL for ZIP codes (2023)
    url = "https://www2.census.gov/geo/tiger/TIGER2023/ZCTA520/tl_2023_us_zcta520.zip"
    
    print(f"Downloading from: {url}")
    print("Note: This is a large file (~250MB) containing all US ZIP codes")
    
    try:
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get('content-length', 0))
        
        zip_file = "census_zip_codes.zip"
        downloaded = 0
        
        with open(zip_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"Progress: {percent:.1f}%", end='\r')
        
        print(f"\nDownloaded: {zip_file}")
        
        # Extract the shapefile
        print("Extracting ZIP code boundaries...")
        with zipfile.ZipFile(zip_file, 'r') as z:
            z.extractall('census_boundaries')
        
        print("Extracted census boundaries to ./census_boundaries/")
        return True
        
    except Exception as e:
        print(f"Error downloading Census data: {e}")
        return False

def process_alice_excel(excel_path):
    """
    Process the downloaded ALICE Excel file
    """
    print(f"\nProcessing ALICE Excel file: {excel_path}")
    
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        print(f"Loaded {len(df)} rows")
        print("\nColumns found:")
        for col in df.columns:
            print(f"  - {col}")
        
        # Clean column names
        df.columns = [col.strip().replace(' ', '_').replace('/', '_') for col in df.columns]
        
        # Look for ZIP code column
        zip_cols = [col for col in df.columns if 'ZIP' in col.upper() or 'ZCTA' in col.upper()]
        if zip_cols:
            print(f"\nFound ZIP code column: {zip_cols[0]}")
            df['ZIP_CODE'] = df[zip_cols[0]].astype(str).str.zfill(5)
        
        # Look for ALICE-related columns
        alice_cols = [col for col in df.columns if 'ALICE' in col.upper()]
        poverty_cols = [col for col in df.columns if 'POVERTY' in col.upper()]
        combined_cols = [col for col in df.columns if 'COMBINED' in col.upper() or 'STRUGGLING' in col.upper()]
        
        print(f"\nFound ALICE columns: {alice_cols}")
        print(f"Found Poverty columns: {poverty_cols}")
        print(f"Found Combined columns: {combined_cols}")
        
        # Save processed data
        output_file = 'florida_alice_zip_processed.csv'
        df.to_csv(output_file, index=False)
        print(f"\nSaved processed data to: {output_file}")
        
        return df
        
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        return None

def create_arcgis_geojson(alice_df, include_demographics=True):
    """
    Create ArcGIS-ready GeoJSON with ALICE ZIP code data
    """
    print("\nCreating ArcGIS GeoJSON...")
    
    # Note: For actual boundaries, you'd need to merge with Census TIGER files
    # This creates the structure ready for merging
    
    features = []
    
    for idx, row in alice_df.iterrows():
        feature = {
            "type": "Feature",
            "properties": {},
            "geometry": None  # Will be added when merged with boundaries
        }
        
        # Add all properties from the DataFrame
        for col in alice_df.columns:
            value = row[col]
            # Convert NaN to None for JSON compatibility
            if pd.isna(value):
                value = None
            elif isinstance(value, (int, float)):
                value = round(float(value), 2) if not pd.isna(value) else None
            else:
                value = str(value)
            
            feature["properties"][col] = value
        
        features.append(feature)
    
    geojson = {
        "type": "FeatureCollection",
        "name": "Florida_ALICE_ZIP_Codes",
        "crs": {
            "type": "name",
            "properties": {
                "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
            }
        },
        "features": features
    }
    
    # Save the GeoJSON structure
    output_file = 'florida_alice_zip_attributes.geojson'
    with open(output_file, 'w') as f:
        json.dump(geojson, f, indent=2)
    
    print(f"Created GeoJSON structure: {output_file}")
    print(f"Total features: {len(features)}")
    
    return geojson

def main():
    print("="*60)
    print("FLORIDA ZIP CODE ALICE DATA PROCESSOR")
    print("="*60)
    
    # Step 1: Check for Excel file
    excel_files = list(Path('.').glob('*alice*zip*.xlsx')) + \
                  list(Path('.').glob('*florida*.xlsx')) + \
                  list(Path('.').glob('*ZIP*.xlsx'))
    
    if excel_files:
        print(f"\nFound Excel file: {excel_files[0]}")
        alice_df = process_alice_excel(excel_files[0])
    else:
        print("\n" + "!"*60)
        print("NO EXCEL FILE FOUND!")
        print("!"*60)
        print("\nPlease:")
        print("1. Go to: https://www.unitedforalice.org/county-reports/florida")
        print("2. Select 'ZIP Codes' in Sub-County Geographies")
        print("3. Download the Excel file")
        print("4. Place it in this directory and run the script again")
        return
    
    if alice_df is not None:
        # Step 2: Create GeoJSON structure
        geojson = create_arcgis_geojson(alice_df)
        
        # Step 3: Instructions for getting boundaries
        print("\n" + "="*60)
        print("NEXT STEPS FOR COMPLETE GEOJSON WITH BOUNDARIES:")
        print("="*60)
        print("\nOption 1: Download Census ZIP boundaries")
        print("  Run: python process_florida_zip_alice.py --download-boundaries")
        print("\nOption 2: Use ArcGIS Online")
        print("  1. Upload florida_alice_zip_attributes.geojson to ArcGIS")
        print("  2. Use 'Join Features' with USA ZIP Code boundaries layer")
        print("  3. Join on ZIP_CODE field")
        print("\nOption 3: Use your dashboard")
        print("  The processed CSV can be integrated into your existing dashboard")
        
        # Step 4: Summary statistics
        if 'ZIP_CODE' in alice_df.columns:
            print("\n" + "="*60)
            print("DATA SUMMARY:")
            print("="*60)
            print(f"Total ZIP codes: {len(alice_df)}")
            print(f"ZIP codes with data: {alice_df['ZIP_CODE'].notna().sum()}")
            
            # Show sample of data
            print("\nSample data (first 5 ZIP codes):")
            print(alice_df.head()[['ZIP_CODE'] + [col for col in alice_df.columns if 'ALICE' in col.upper() or 'POVERTY' in col.upper()]])

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and '--download-boundaries' in sys.argv:
        download_census_zip_boundaries()
    else:
        main()