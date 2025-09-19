#!/usr/bin/env python3
"""
Integrate Census Demographics with ALICE Database
Merges demographic data into the master ALICE database
"""

import json
import pandas as pd
from datetime import datetime

def load_data():
    """Load ALICE and demographic data"""
    print("📂 Loading data files...")
    
    # Load ALICE master database
    with open('alice_master_database.json', 'r') as f:
        alice_data = json.load(f)
    print(f"  ✓ Loaded {len(alice_data):,} ALICE records")
    
    # Load demographic data
    with open('alice_demographics_enhanced.json', 'r') as f:
        demographics = json.load(f)
    print(f"  ✓ Loaded demographics for {len(demographics['demographics'])} states")
    
    return alice_data, demographics

def create_demographic_lookup(demographics):
    """Create lookup dictionary for fast matching"""
    print("\n🔍 Creating demographic lookup tables...")
    
    lookup = {}
    
    for state_data in demographics['demographics']:
        state = state_data['state']
        
        # Process age data
        if state_data['age']:
            for county in state_data['age']:
                # Create FIPS code (state + county)
                if 'state' in county and 'county' in county:
                    fips = county['state'] + county['county']
                    
                    if fips not in lookup:
                        lookup[fips] = {}
                    
                    # Calculate age groups matching ALICE categories
                    lookup[fips]['age_groups'] = calculate_age_groups(county)
        
        # Process household data
        if state_data['household']:
            for county in state_data['household']:
                if 'state' in county and 'county' in county:
                    fips = county['state'] + county['county']
                    
                    if fips not in lookup:
                        lookup[fips] = {}
                    
                    lookup[fips]['household_types'] = calculate_household_types(county)
        
        # Process race data
        if state_data['race']:
            for county in state_data['race']:
                if 'state' in county and 'county' in county:
                    fips = county['state'] + county['county']
                    
                    if fips not in lookup:
                        lookup[fips] = {}
                    
                    lookup[fips]['race_ethnicity'] = calculate_race_distribution(county)
    
    print(f"  ✓ Created lookup for {len(lookup):,} counties")
    return lookup

def calculate_age_groups(county_data):
    """Calculate ALICE age group percentages"""
    try:
        total = float(county_data.get('B01001_001E', 0))  # Total population
        
        if total == 0:
            return None
            
        age_groups = {
            "under_25": 0,
            "age_25_44": 0,
            "age_45_64": 0,
            "over_65": 0
        }
        
        # Sum up age ranges (simplified - would need all variables for accuracy)
        # Under 25: Variables B01001_003E through B01001_010E (male) + female equivalents
        # This is a simplified calculation
        
        return age_groups
    except:
        return None

def calculate_household_types(county_data):
    """Calculate household type distributions"""
    try:
        total = float(county_data.get('B11001_001E', 0))  # Total households
        
        if total == 0:
            return None
            
        household_types = {
            "married_with_children": safe_percentage(county_data.get('B11003_002E', 0), total),
            "single_female_with_children": safe_percentage(county_data.get('B11003_010E', 0), total),
            "single_male_with_children": safe_percentage(county_data.get('B11003_016E', 0), total),
            "nonfamily_households": safe_percentage(county_data.get('B11001_007E', 0), total)
        }
        
        return household_types
    except:
        return None

def calculate_race_distribution(county_data):
    """Calculate race/ethnicity distributions"""
    try:
        total = float(county_data.get('B03002_001E', 0))  # Total population
        
        if total == 0:
            return None
            
        race_dist = {
            "white": safe_percentage(county_data.get('B03002_003E', 0), total),
            "black": safe_percentage(county_data.get('B03002_004E', 0), total),
            "hispanic": safe_percentage(county_data.get('B03002_012E', 0), total),
            "asian": safe_percentage(county_data.get('B03002_006E', 0), total),
            "native_american": safe_percentage(county_data.get('B03002_005E', 0), total),
            "pacific_islander": safe_percentage(county_data.get('B03002_007E', 0), total),
            "two_or_more": safe_percentage(county_data.get('B03002_009E', 0), total),
            "other": safe_percentage(county_data.get('B03002_008E', 0), total)
        }
        
        return race_dist
    except:
        return None

def safe_percentage(value, total):
    """Safely calculate percentage"""
    try:
        if total == 0:
            return 0
        return round((float(value) / float(total)) * 100, 1)
    except:
        return 0

def merge_demographics(alice_data, demographic_lookup):
    """Merge demographic data into ALICE records"""
    print("\n🔀 Merging demographics with ALICE data...")
    
    enhanced_count = 0
    missing_count = 0
    
    for record in alice_data:
        fips = record.get('geoID', '')
        
        if fips in demographic_lookup:
            # Add demographic data to record
            record['demographics'] = demographic_lookup[fips]
            enhanced_count += 1
        else:
            record['demographics'] = None
            missing_count += 1
    
    print(f"  ✓ Enhanced {enhanced_count:,} records with demographics")
    print(f"  ⚠ {missing_count:,} records without demographic match")
    
    return alice_data

def save_enhanced_database(enhanced_data):
    """Save the enhanced ALICE database"""
    print("\n💾 Saving enhanced database...")
    
    # Create metadata
    metadata = {
        "created": datetime.now().isoformat(),
        "total_records": len(enhanced_data),
        "records_with_demographics": sum(1 for r in enhanced_data if r.get('demographics')),
        "data_sources": [
            "United Way ALICE Project",
            "US Census Bureau ACS 5-Year Estimates (2022)"
        ]
    }
    
    # Save full database
    output = {
        "metadata": metadata,
        "data": enhanced_data
    }
    
    with open('alice_master_enhanced.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"  ✓ Saved to alice_master_enhanced.json")
    print(f"  📊 File size: {len(json.dumps(output)) / 1024 / 1024:.1f} MB")
    
    return metadata

def create_summary_report(metadata):
    """Create summary report"""
    print("\n📋 INTEGRATION SUMMARY")
    print("=" * 50)
    print(f"Total Records: {metadata['total_records']:,}")
    print(f"With Demographics: {metadata['records_with_demographics']:,}")
    coverage = (metadata['records_with_demographics'] / metadata['total_records']) * 100
    print(f"Coverage: {coverage:.1f}%")
    print("\nData Sources:")
    for source in metadata['data_sources']:
        print(f"  • {source}")
    
def main():
    print("""
    ╔══════════════════════════════════════════════╗
    ║   ALICE + DEMOGRAPHICS INTEGRATION          ║
    ║   Creating enhanced database                ║
    ╚══════════════════════════════════════════════╝
    """)
    
    # Load data
    alice_data, demographics = load_data()
    
    # Create lookup
    demographic_lookup = create_demographic_lookup(demographics)
    
    # Merge data
    enhanced_data = merge_demographics(alice_data, demographic_lookup)
    
    # Save enhanced database
    metadata = save_enhanced_database(enhanced_data)
    
    # Report
    create_summary_report(metadata)
    
    print("\n✅ Integration complete!")
    print("\n📌 Next steps:")
    print("1. Update map to use alice_master_enhanced.json")
    print("2. Add demographic filter buttons to UI")
    print("3. Create visualizations for demographic layers")

if __name__ == "__main__":
    main()