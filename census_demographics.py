#!/usr/bin/env python3
"""
Census Bureau Demographic Data Fetcher
Gets the same demographic breakdowns ALICE uses, directly from Census API
"""

import requests
import json
import pandas as pd
from datetime import datetime
import time

class CensusDemographics:
    def __init__(self):
        # Note: Get free API key at https://api.census.gov/data/key_signup.html
        self.api_key = "6f6062548049a9478328104582e65c604fd4432d"
        self.base_url = "https://api.census.gov/data"
        
        # Map our ALICE states to FIPS codes
        self.state_fips = {
            "Alabama": "01", "Arkansas": "05", "Colorado": "08",
            "Connecticut": "09", "Delaware": "10", "Florida": "12",
            "Georgia": "13", "Hawaii": "15", "Idaho": "16",
            "Illinois": "17", "Indiana": "18", "Iowa": "19",
            "Kansas": "20", "Louisiana": "22", "Maine": "23",
            "Maryland": "24", "Michigan": "26", "Minnesota": "27",
            "Mississippi": "28", "New Jersey": "34", "New Mexico": "35",
            "New York": "36", "North Carolina": "37", "Ohio": "39",
            "Oregon": "41", "Pennsylvania": "42", "South Carolina": "45",
            "Tennessee": "47", "Texas": "48", "Virginia": "51",
            "Washington": "53", "West Virginia": "54"
        }
        
        self.demographic_data = []
        
    def get_age_demographics(self, state_name, state_fips):
        """Get age group demographics for a state"""
        print(f"  📊 Fetching age demographics for {state_name}...")
        
        # ACS 5-year estimates endpoint
        endpoint = "/2022/acs/acs5"
        
        # Age group variables
        age_variables = {
            "B01001_001E": "Total_Population",
            "B01001_003E": "Male_Under_5",
            "B01001_004E": "Male_5_to_9",
            "B01001_005E": "Male_10_to_14",
            "B01001_006E": "Male_15_to_17",
            "B01001_007E": "Male_18_to_19",
            "B01001_008E": "Male_20",
            "B01001_009E": "Male_21",
            "B01001_010E": "Male_22_to_24",
            "B01001_011E": "Male_25_to_29",
            "B01001_012E": "Male_30_to_34",
            "B01001_013E": "Male_35_to_39",
            "B01001_014E": "Male_40_to_44",
            "B01001_015E": "Male_45_to_49",
            "B01001_016E": "Male_50_to_54",
            "B01001_017E": "Male_55_to_59",
            "B01001_018E": "Male_60_to_61",
            "B01001_019E": "Male_62_to_64",
            "B01001_020E": "Male_65_to_66",
            "B01001_021E": "Male_67_to_69",
            "B01001_022E": "Male_70_to_74",
            "B01001_023E": "Male_75_to_79",
            "B01001_024E": "Male_80_to_84",
            "B01001_025E": "Male_85_plus"
        }
        
        # Also get female counts (B01001_027E through B01001_049E)
        
        url = f"{self.base_url}{endpoint}"
        params = {
            "get": ",".join(list(age_variables.keys())[:10]),  # First 10 variables
            "for": "county:*",
            "in": f"state:{state_fips}"
        }
        
        params["key"] = self.api_key
            
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self.process_age_data(data, state_name)
            else:
                print(f"    ⚠️  API returned {response.status_code}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            
        return None
    
    def process_age_data(self, data, state_name):
        """Process age data from Census API"""
        if not data or len(data) < 2:
            return None
            
        headers = data[0]
        rows = data[1:]
        
        processed = []
        for row in rows:
            county_data = dict(zip(headers, row))
            processed.append(county_data)
            
        return processed
        
    def get_household_demographics(self, state_name, state_fips):
        """Get household type demographics"""
        print(f"  🏠 Fetching household demographics for {state_name}...")
        
        endpoint = "/2022/acs/acs5"
        
        # Household type variables
        household_variables = {
            "B11001_001E": "Total_Households",
            "B11001_002E": "Family_Households",
            "B11001_003E": "Married_Couple_Family",
            "B11001_005E": "Male_Householder_No_Spouse",
            "B11001_006E": "Female_Householder_No_Spouse",
            "B11001_007E": "Nonfamily_Households",
            "B11003_001E": "Total_Families",
            "B11003_002E": "Married_With_Children",
            "B11003_003E": "Married_No_Children",
            "B11003_010E": "Single_Female_With_Children",
            "B11003_016E": "Single_Male_With_Children"
        }
        
        url = f"{self.base_url}{endpoint}"
        params = {
            "get": ",".join(list(household_variables.keys())[:8]),
            "for": "county:*",
            "in": f"state:{state_fips}"
        }
        
        params["key"] = self.api_key
            
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self.process_household_data(data, state_name)
            else:
                print(f"    ⚠️  API returned {response.status_code}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            
        return None
    
    def process_household_data(self, data, state_name):
        """Process household data from Census API"""
        if not data or len(data) < 2:
            return None
            
        headers = data[0]
        rows = data[1:]
        
        processed = []
        for row in rows:
            county_data = dict(zip(headers, row))
            processed.append(county_data)
            
        return processed
        
    def get_race_demographics(self, state_name, state_fips):
        """Get race/ethnicity demographics"""
        print(f"  🌍 Fetching race/ethnicity demographics for {state_name}...")
        
        endpoint = "/2022/acs/acs5"
        
        # Race variables
        race_variables = {
            "B03002_001E": "Total_Population",
            "B03002_003E": "White_Not_Hispanic",
            "B03002_004E": "Black_Not_Hispanic",
            "B03002_005E": "American_Indian_Not_Hispanic",
            "B03002_006E": "Asian_Not_Hispanic",
            "B03002_007E": "Pacific_Islander_Not_Hispanic",
            "B03002_008E": "Other_Race_Not_Hispanic",
            "B03002_009E": "Two_Or_More_Races_Not_Hispanic",
            "B03002_012E": "Hispanic_Any_Race"
        }
        
        url = f"{self.base_url}{endpoint}"
        params = {
            "get": ",".join(list(race_variables.keys())),
            "for": "county:*",
            "in": f"state:{state_fips}"
        }
        
        params["key"] = self.api_key
            
        try:
            response = requests.get(url, params=params)
            if response.status_code == 200:
                data = response.json()
                return self.process_race_data(data, state_name)
            else:
                print(f"    ⚠️  API returned {response.status_code}")
        except Exception as e:
            print(f"    ❌ Error: {e}")
            
        return None
    
    def process_race_data(self, data, state_name):
        """Process race data from Census API"""
        if not data or len(data) < 2:
            return None
            
        headers = data[0]
        rows = data[1:]
        
        processed = []
        for row in rows:
            county_data = dict(zip(headers, row))
            processed.append(county_data)
            
        return processed
        
    def aggregate_to_alice_categories(self, raw_data):
        """Convert Census categories to ALICE categories"""
        
        alice_categories = {
            "age_groups": {
                "Under 25": ["Under_5", "5_to_9", "10_to_14", "15_to_17", "18_to_19", "20", "21", "22_to_24"],
                "25 to 44": ["25_to_29", "30_to_34", "35_to_39", "40_to_44"],
                "45 to 64": ["45_to_49", "50_to_54", "55_to_59", "60_to_61", "62_to_64"],
                "Over 65": ["65_to_66", "67_to_69", "70_to_74", "75_to_79", "80_to_84", "85_plus"]
            },
            "household_types": {
                "Married With Children": ["Married_With_Children"],
                "Single Female With Children": ["Single_Female_With_Children"],
                "Single Male With Children": ["Single_Male_With_Children"],
                "Single or Cohabitating Under 65": ["Nonfamily_Households"]  # Approximation
            },
            "race_ethnicity": {
                "White": ["White_Not_Hispanic"],
                "Black": ["Black_Not_Hispanic"],
                "Hispanic": ["Hispanic_Any_Race"],
                "Asian": ["Asian_Not_Hispanic"],
                "Hawaiian": ["Pacific_Islander_Not_Hispanic"],
                "Two or More Races": ["Two_Or_More_Races_Not_Hispanic"],
                "AI/AN": ["American_Indian_Not_Hispanic"]
            }
        }
        
        return alice_categories
        
    def fetch_all_demographics(self):
        """Fetch demographics for all states"""
        print("\n📊 FETCHING CENSUS DEMOGRAPHICS")
        print("=" * 60)
        
        print("✅ API Key loaded successfully!")
            
        # Fetch for each state
        total_states = len(self.state_fips)
        for idx, (state_name, state_fips) in enumerate(self.state_fips.items(), 1):
            print(f"\n📍 Processing {state_name} ({idx}/{total_states})...")
            
            # Get demographics
            age_data = self.get_age_demographics(state_name, state_fips)
            household_data = self.get_household_demographics(state_name, state_fips)
            race_data = self.get_race_demographics(state_name, state_fips)
            
            self.demographic_data.append({
                "state": state_name,
                "state_fips": state_fips,
                "age": age_data,
                "household": household_data,
                "race": race_data
            })
            
            time.sleep(0.5)  # Be respectful to API
            
    def save_demographics(self):
        """Save demographic data to files"""
        
        # Create enhanced database structure
        enhanced_db = {
            "created": datetime.now().isoformat(),
            "source": "US Census Bureau ACS 5-Year Estimates",
            "demographics": self.demographic_data,
            "categories": self.aggregate_to_alice_categories(None)
        }
        
        # Save to JSON
        with open('alice_demographics_enhanced.json', 'w') as f:
            json.dump(enhanced_db, f, indent=2)
            
        print(f"\n✅ Saved enhanced demographics to alice_demographics_enhanced.json")
        
    def create_integration_script(self):
        """Create script to integrate demographics with existing ALICE data"""
        
        script = """
# Integration Script: Merge Demographics with ALICE Data

import json
import pandas as pd

# Load existing ALICE data
with open('alice_master_database.json', 'r') as f:
    alice_data = json.load(f)

# Load new demographics
with open('alice_demographics_enhanced.json', 'r') as f:
    demographics = json.load(f)

# Create enhanced records
enhanced_records = []

for alice_record in alice_data:
    # Find matching demographic data
    county_demographics = find_demographics(
        alice_record['geoID'],
        demographics
    )
    
    # Merge data
    enhanced_record = {
        **alice_record,
        'demographics': county_demographics
    }
    
    enhanced_records.append(enhanced_record)

# Save enhanced database
with open('alice_master_enhanced.json', 'w') as f:
    json.dump(enhanced_records, f, indent=2)

print(f"✅ Created enhanced database with {len(enhanced_records)} records")
"""
        
        with open('integrate_demographics.py', 'w') as f:
            f.write(script)
            
        print("📝 Created integrate_demographics.py script")

def main():
    print("""
    ╔══════════════════════════════════════════════╗
    ║   CENSUS BUREAU DEMOGRAPHIC FETCHER         ║
    ║   Direct access to source data              ║
    ╚══════════════════════════════════════════════╝
    """)
    
    fetcher = CensusDemographics()
    
    # Fetch all demographics
    fetcher.fetch_all_demographics()
    
    # Save results
    if fetcher.demographic_data:
        fetcher.save_demographics()
        fetcher.create_integration_script()
    
    print("\n" + "="*60)
    print("📋 NEXT STEPS:")
    print("1. Get free Census API key (takes 1 minute)")
    print("2. Run this script with the key")
    print("3. Integrate demographics into ALICE database")
    print("4. Update map to show demographic layers")

if __name__ == "__main__":
    main()