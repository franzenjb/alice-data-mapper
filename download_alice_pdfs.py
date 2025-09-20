#!/usr/bin/env python3
"""
Download all ALICE state PDF reports
"""

import requests
import os
from pathlib import Path
import time

def download_alice_reports():
    """Download all ALICE state PDF reports"""
    
    # Create folder on Desktop
    desktop_path = Path.home() / "Desktop" / "ALICE State Reports 2025"
    desktop_path.mkdir(exist_ok=True)
    
    print(f"📁 Creating folder: {desktop_path}")
    
    # Base URL for ALICE reports
    base_url = "https://www.unitedforalice.org/Attachments/AllReports/"
    
    # List of states with reports (based on website data)
    states_with_reports = [
        ("Alabama", "2025 ALICE Report - Alabama.pdf"),
        ("Arkansas", "2025 ALICE Report - Arkansas.pdf"),
        ("Colorado", "2025 ALICE Report - Colorado.pdf"),
        ("Connecticut", "2025 ALICE Report - Connecticut.pdf"),
        ("Delaware", "2025 ALICE Report - Delaware.pdf"),
        ("DC Metro", "2025 ALICE Report - DC Metro Area.pdf"),
        ("Florida", "2025 ALICE Report - Florida.pdf"),
        ("Georgia", "2025 ALICE Report - Georgia.pdf"),
        ("Hawaii", "2025 ALICE Report - Hawaii.pdf"),
        ("Idaho", "2025 ALICE Report - Idaho.pdf"),
        ("Illinois", "2025 ALICE Report - Illinois.pdf"),
        ("Indiana", "2025 ALICE Report - Indiana.pdf"),
        ("Iowa", "2025 ALICE Report - Iowa.pdf"),
        ("Kansas", "2025 ALICE Report - Kansas.pdf"),
        ("Louisiana", "2025 ALICE Report - Louisiana.pdf"),
        ("Maine", "2025 ALICE Report - Maine.pdf"),
        ("Maryland", "2025 ALICE Report - Maryland.pdf"),
        ("Michigan", "2025 ALICE Report - Michigan.pdf"),
        ("Minnesota", "2025 ALICE Report - Minnesota.pdf"),
        ("Mississippi", "2025 ALICE Report - Mississippi.pdf"),
        ("New Jersey", "2025 ALICE Report - New Jersey.pdf"),
        ("New Mexico", "2025 ALICE Report - New Mexico.pdf"),
        ("New York", "2025 ALICE Report - New York.pdf"),
        ("North Carolina", "2025 ALICE Report - North Carolina.pdf"),
        ("Ohio", "2025 ALICE Report - Ohio.pdf"),
        ("Oregon", "2025 ALICE Report - Oregon.pdf"),
        ("Pennsylvania", "2025 ALICE Report - Pennsylvania.pdf"),
        ("South Carolina", "2025 ALICE Report - South Carolina.pdf"),
        ("Tennessee", "2025 ALICE Report - Tennessee.pdf"),
        ("Texas", "2025 ALICE Report - Texas.pdf"),
        ("Virginia", "2025 ALICE Report - Virginia.pdf"),
        ("Washington", "2025 ALICE Report - Washington.pdf"),
        ("West Virginia", "2025 ALICE Report - West Virginia.pdf"),
        ("Wisconsin", "2025 ALICE Report - Wisconsin.pdf")
    ]
    
    # Also try to get the national report
    national_reports = [
        ("National Overview 2023", "2023 ALICE National Report.pdf"),
        ("National Overview 2024", "2024 ALICE National Report.pdf")
    ]
    
    all_reports = states_with_reports + national_reports
    
    print(f"\n📊 Downloading {len(all_reports)} reports...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    })
    
    downloaded = 0
    failed = []
    
    for state_name, filename in all_reports:
        # Try different URL patterns
        urls_to_try = [
            f"{base_url}{filename}",
            f"https://www.unitedforalice.org/Attachments/{filename}",
            f"https://www.unitedforalice.org/Attachments/StateReports/{filename}",
            # URL encode spaces
            f"{base_url}{filename.replace(' ', '%20')}",
            f"https://www.unitedforalice.org/Attachments/{filename.replace(' ', '%20')}"
        ]
        
        success = False
        for url in urls_to_try:
            try:
                print(f"📥 Downloading {state_name}...", end=" ")
                response = session.get(url, timeout=30)
                
                if response.status_code == 200 and len(response.content) > 1000:
                    # Save the file
                    output_path = desktop_path / filename
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    
                    file_size_mb = len(response.content) / (1024 * 1024)
                    print(f"✅ ({file_size_mb:.1f} MB)")
                    downloaded += 1
                    success = True
                    break
                    
            except Exception as e:
                continue
        
        if not success:
            print(f"❌ Failed")
            failed.append(state_name)
        
        # Be respectful to the server
        time.sleep(1)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successfully downloaded: {downloaded} reports")
    if failed:
        print(f"   ❌ Failed to download: {len(failed)} reports")
        print(f"      {', '.join(failed)}")
    
    print(f"\n📁 Reports saved to: {desktop_path}")
    
    # Create a README file
    readme_path = desktop_path / "README.txt"
    with open(readme_path, 'w') as f:
        f.write("ALICE State Reports Collection\n")
        f.write("="*40 + "\n\n")
        f.write(f"Downloaded: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total Reports: {downloaded}\n\n")
        f.write("These reports contain comprehensive data about ALICE\n")
        f.write("(Asset Limited, Income Constrained, Employed) households\n")
        f.write("in each state.\n\n")
        f.write("Source: United For ALICE (www.unitedforalice.org)\n")
        f.write("\nStates with reports:\n")
        for state, _ in states_with_reports:
            if state not in failed:
                f.write(f"  • {state}\n")
    
    print(f"📝 Created README.txt")
    
    return desktop_path

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   ALICE PDF REPORT DOWNLOADER             ║
    ║   Downloading all state reports            ║
    ╚════════════════════════════════════════════╝
    """)
    
    folder_path = download_alice_reports()
    
    print(f"""
    ✅ Download complete!
    
    📂 Open folder: {folder_path}
    
    Note: Some reports may not be available yet.
    Check www.unitedforalice.org for updates.
    """)