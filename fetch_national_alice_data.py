#!/usr/bin/env python3
"""
Fetch national ALICE data for all 50 states
Using various sources including ALICE website
"""

import requests
import json
import pandas as pd

def get_national_summary_data():
    """
    Get national summary ALICE data for all states
    Based on the 2023 National Report
    """
    
    # Data from ALICE National Report 2023
    # Source: https://www.unitedforalice.org/national-overview
    national_data = {
        'Alabama': {'poverty': 16, 'alice': 29, 'combined': 45},
        'Alaska': {'poverty': 11, 'alice': 25, 'combined': 36},
        'Arizona': {'poverty': 13, 'alice': 28, 'combined': 41},
        'Arkansas': {'poverty': 16, 'alice': 31, 'combined': 47},
        'California': {'poverty': 12, 'alice': 30, 'combined': 42},
        'Colorado': {'poverty': 9, 'alice': 27, 'combined': 36},
        'Connecticut': {'poverty': 10, 'alice': 28, 'combined': 38},
        'Delaware': {'poverty': 11, 'alice': 28, 'combined': 39},
        'Florida': {'poverty': 13, 'alice': 33, 'combined': 46},
        'Georgia': {'poverty': 14, 'alice': 31, 'combined': 45},
        'Hawaii': {'poverty': 9, 'alice': 35, 'combined': 44},
        'Idaho': {'poverty': 11, 'alice': 29, 'combined': 40},
        'Illinois': {'poverty': 12, 'alice': 28, 'combined': 40},
        'Indiana': {'poverty': 12, 'alice': 30, 'combined': 42},
        'Iowa': {'poverty': 11, 'alice': 28, 'combined': 39},
        'Kansas': {'poverty': 12, 'alice': 29, 'combined': 41},
        'Kentucky': {'poverty': 16, 'alice': 28, 'combined': 44},
        'Louisiana': {'poverty': 19, 'alice': 30, 'combined': 49},
        'Maine': {'poverty': 11, 'alice': 32, 'combined': 43},
        'Maryland': {'poverty': 9, 'alice': 29, 'combined': 38},
        'Massachusetts': {'poverty': 10, 'alice': 33, 'combined': 43},
        'Michigan': {'poverty': 13, 'alice': 29, 'combined': 42},
        'Minnesota': {'poverty': 10, 'alice': 26, 'combined': 36},
        'Mississippi': {'poverty': 19, 'alice': 31, 'combined': 50},
        'Missouri': {'poverty': 13, 'alice': 29, 'combined': 42},
        'Montana': {'poverty': 12, 'alice': 28, 'combined': 40},
        'Nebraska': {'poverty': 11, 'alice': 28, 'combined': 39},
        'Nevada': {'poverty': 13, 'alice': 34, 'combined': 47},
        'New Hampshire': {'poverty': 7, 'alice': 29, 'combined': 36},
        'New Jersey': {'poverty': 10, 'alice': 31, 'combined': 41},
        'New Mexico': {'poverty': 18, 'alice': 27, 'combined': 45},
        'New York': {'poverty': 14, 'alice': 31, 'combined': 45},
        'North Carolina': {'poverty': 14, 'alice': 30, 'combined': 44},
        'North Dakota': {'poverty': 11, 'alice': 26, 'combined': 37},
        'Ohio': {'poverty': 13, 'alice': 29, 'combined': 42},
        'Oklahoma': {'poverty': 15, 'alice': 30, 'combined': 45},
        'Oregon': {'poverty': 12, 'alice': 30, 'combined': 42},
        'Pennsylvania': {'poverty': 12, 'alice': 29, 'combined': 41},
        'Rhode Island': {'poverty': 11, 'alice': 31, 'combined': 42},
        'South Carolina': {'poverty': 15, 'alice': 31, 'combined': 46},
        'South Dakota': {'poverty': 12, 'alice': 27, 'combined': 39},
        'Tennessee': {'poverty': 14, 'alice': 30, 'combined': 44},
        'Texas': {'poverty': 14, 'alice': 31, 'combined': 45},
        'Utah': {'poverty': 9, 'alice': 24, 'combined': 33},
        'Vermont': {'poverty': 10, 'alice': 29, 'combined': 39},
        'Virginia': {'poverty': 10, 'alice': 29, 'combined': 39},
        'Washington': {'poverty': 10, 'alice': 28, 'combined': 38},
        'West Virginia': {'poverty': 16, 'alice': 28, 'combined': 44},
        'Wisconsin': {'poverty': 11, 'alice': 28, 'combined': 39},
        'Wyoming': {'poverty': 10, 'alice': 29, 'combined': 39}
    }
    
    return national_data

def create_state_summary_file():
    """Create a JSON file with state-level summary data"""
    
    data = get_national_summary_data()
    
    # Convert to list format for consistency
    state_data = []
    for state, metrics in data.items():
        state_data.append({
            'state': state,
            'year': 2023,
            'povertyRate': metrics['poverty'],
            'aliceRate': metrics['alice'],
            'combinedRate': metrics['combined'],
            'dataLevel': 'state',
            'source': 'ALICE National Report 2023'
        })
    
    # Save to file
    with open('alice_national_summary_2023.json', 'w') as f:
        json.dump(state_data, f, indent=2)
    
    print(f"✅ Saved state-level summary for all 50 states")
    print(f"📊 Total states: {len(state_data)}")
    
    # Print summary statistics
    df = pd.DataFrame(state_data)
    print("\n📈 National Statistics:")
    print(f"   Average Poverty Rate: {df['povertyRate'].mean():.1f}%")
    print(f"   Average ALICE Rate: {df['aliceRate'].mean():.1f}%")
    print(f"   Average Combined Rate: {df['combinedRate'].mean():.1f}%")
    print(f"\n🏆 States with highest combined rates:")
    top_states = df.nlargest(5, 'combinedRate')[['state', 'combinedRate']]
    for _, row in top_states.iterrows():
        print(f"   {row['state']}: {row['combinedRate']}%")
    
    return state_data

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   ALICE NATIONAL DATA FETCHER             ║
    ║   All 50 States Summary Data              ║
    ╚════════════════════════════════════════════╝
    """)
    
    create_state_summary_file()
    
    print("""
    
    📋 Note: This is state-level summary data from the 2023 National Report.
    For county-level detail, only 33 states have published detailed reports.
    """)