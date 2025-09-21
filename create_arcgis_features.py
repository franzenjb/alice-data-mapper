#!/usr/bin/env python3
"""
Convert ALICE data to ArcGIS Feature Layer format
Creates GeoJSON files ready for import into ArcGIS
"""

import json
import requests
from datetime import datetime

print("Creating ArcGIS-compatible feature layers from ALICE data...")

# Load ALICE data
print("Loading ALICE data...")
with open('alice_master_database.json', 'r') as f:
    alice_data = json.load(f)

# Download county boundaries GeoJSON
print("Downloading county boundaries...")
counties_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
response = requests.get(counties_url)
counties_geojson = response.json()

# Create lookup for ALICE data by geoID and year
alice_lookup = {}
for record in alice_data:
    if record['geoLevel'] == 'county':
        key = f"{record['geoID']}_{record['year']}"
        alice_lookup[key] = record

# Get unique years
years = sorted(set(record['year'] for record in alice_data if record['geoLevel'] == 'county'))
print(f"Found data for years: {years}")

# Create feature collection for each year
for year in years:
    print(f"\nProcessing year {year}...")
    
    features = []
    matched = 0
    unmatched = 0
    
    for county_feature in counties_geojson['features']:
        # Get FIPS code
        state_fp = county_feature['properties'].get('STATE', '')
        county_fp = county_feature['properties'].get('COUNTY', '')
        fips = f"{state_fp}{county_fp}"
        
        # Pad with leading zeros if needed
        if len(fips) == 4:
            fips = '0' + fips
        elif len(fips) == 3:
            fips = '00' + fips
            
        # Look up ALICE data
        key = f"{fips}_{year}"
        if key in alice_lookup:
            alice_record = alice_lookup[key]
            matched += 1
            
            # Create enhanced properties
            properties = {
                # Geographic identifiers
                'GEOID': fips,
                'STATE_FP': state_fp,
                'COUNTY_FP': county_fp,
                'NAME': alice_record.get('county', ''),
                'STATE': alice_record.get('state', ''),
                'GEO_LABEL': alice_record.get('geoDisplayLabel', ''),
                
                # ALICE metrics
                'YEAR': year,
                'TOTAL_HH': alice_record.get('totalHouseholds', 0),
                'POVERTY_HH': alice_record.get('povertyHouseholds', 0),
                'ALICE_HH': alice_record.get('aliceHouseholds', 0),
                'ABOVE_HH': alice_record.get('aboveAliceHouseholds', 0),
                'POVERTY_RT': float(alice_record.get('povertyRate', 0)),
                'ALICE_RT': float(alice_record.get('aliceRate', 0)),
                'COMBINED_RT': float(alice_record.get('combinedRate', 0)),
                
                # Calculated fields
                'STRUGGLING_HH': alice_record.get('povertyHouseholds', 0) + alice_record.get('aliceHouseholds', 0),
                'STRUGGLING_PCT': float(alice_record.get('combinedRate', 0)),
                
                # Demographic fields (mostly null but structure is there)
                'POV_BLACK': alice_record.get('povertyHH_Black'),
                'POV_HISPANIC': alice_record.get('povertyHH_Hispanic'),
                'POV_WHITE': alice_record.get('povertyHH_White'),
                'ALICE_BLACK': alice_record.get('aliceHH_Black'),
                'ALICE_HISPANIC': alice_record.get('aliceHH_Hispanic'),
                'ALICE_WHITE': alice_record.get('aliceHH_White'),
                
                # Metadata
                'DATA_SOURCE': alice_record.get('dataSource', ''),
                'UPDATED': datetime.now().isoformat()
            }
            
            # Create feature
            feature = {
                'type': 'Feature',
                'geometry': county_feature['geometry'],
                'properties': properties
            }
            features.append(feature)
        else:
            unmatched += 1
    
    # Create feature collection
    feature_collection = {
        'type': 'FeatureCollection',
        'name': f'ALICE_Counties_{year}',
        'crs': {
            'type': 'name',
            'properties': {
                'name': 'EPSG:4326'
            }
        },
        'features': features
    }
    
    # Save to file
    filename = f'alice_counties_{year}.geojson'
    with open(filename, 'w') as f:
        json.dump(feature_collection, f)
    
    print(f"Created {filename}")
    print(f"  - Matched counties: {matched}")
    print(f"  - Unmatched counties: {unmatched}")
    print(f"  - Total features: {len(features)}")

# Create a master file with just 2023 data (most recent)
print("\nCreating master 2023 feature layer...")
with open('alice_counties_2023.geojson', 'r') as f:
    master_data = json.load(f)

master_data['name'] = 'ALICE_Counties_Master'
with open('alice_counties_master.geojson', 'w') as f:
    json.dump(master_data, f)

print("\n✅ ArcGIS Feature Layers Created!")
print("\nFiles created:")
print("  - alice_counties_master.geojson (2023 data - recommended for ArcGIS)")
for year in years:
    print(f"  - alice_counties_{year}.geojson")

print("\n📍 To use in ArcGIS:")
print("1. Open ArcGIS Pro or ArcGIS Online")
print("2. Add Data → Browse to the .geojson files")
print("3. Or publish as a hosted feature layer to ArcGIS Online")
print("\n💡 The files contain:")
print("  - County boundaries (polygons)")
print("  - All ALICE metrics as attributes")
print("  - Ready for symbolization and analysis")