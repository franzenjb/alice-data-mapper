#!/usr/bin/env python3
"""
Download all ALICE state PDF reports with correct URLs
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
    
    # Base URL
    base_url = "https://www.unitedforalice.org"
    
    # Correct URLs for each state report
    reports = [
        ("Alabama", "/Attachments/AllReports/state-of-alice-report-alabama-2025.pdf"),
        ("Arkansas", "/Attachments/AllReports/state-of-alice-report-arkansas-2025.pdf"),
        ("Colorado", "/Attachments/AllReports/state-of-alice-report-colorado-2025.pdf"),
        ("Connecticut", "/Attachments/AllReports/state-of-alice-report-connecticut-2025.pdf"),
        ("Delaware", "/Attachments/AllReports/state-of-alice-report-delaware-2025.pdf"),
        ("DC Metro Area", "/Attachments/AllReports/state-of-alice-report-dc-metro-2025.pdf"),
        ("Florida", "/Attachments/AllReports/state-of-alice-report-florida-2025.pdf"),
        ("Georgia", "/Attachments/AllReports/state-of-alice-report-georgia-2025.pdf"),
        ("Hawaii", "/Attachments/AllReports/state-of-alice-report-hawaii-2025.pdf"),
        ("Idaho", "/Attachments/AllReports/state-of-alice-report-idaho-2025.pdf"),
        ("Illinois", "/Attachments/AllReports/state-of-alice-report-illinois-2025.pdf"),
        ("Indiana", "/Attachments/AllReports/state-of-alice-report-indiana-2025.pdf"),
        ("Iowa", "/Attachments/AllReports/state-of-alice-report-iowa-2025.pdf"),
        ("Kansas", "/Attachments/AllReports/state-of-alice-report-kansas-2025.pdf"),
        ("Louisiana", "/Attachments/AllReports/state-of-alice-report-louisiana-2025.pdf"),
        ("Maine", "/Attachments/AllReports/state-of-alice-report-maine-2025.pdf"),
        ("Maryland", "/Attachments/AllReports/state-of-alice-report-maryland-2025.pdf"),
        ("Michigan", "/Attachments/AllReports/state-of-alice-report-michigan-2025.pdf"),
        ("Minnesota", "/Attachments/AllReports/state-of-alice-report-minnesota-2025.pdf"),
        ("Mississippi", "/Attachments/AllReports/state-of-alice-report-mississippi-2025.pdf"),
        ("New Jersey", "/Attachments/AllReports/state-of-alice-report-new-jersey-2025.pdf"),
        ("New Mexico", "/Attachments/AllReports/state-of-alice-report-new-mexico-2025.pdf"),
        ("New York", "/Attachments/AllReports/state-of-alice-report-new-york-2025.pdf"),
        ("North Carolina", "/Attachments/AllReports/state-of-alice-report-north-carolina-2025.pdf"),
        ("Ohio", "/Attachments/AllReports/state-of-alice-report-ohio-2025.pdf"),
        ("Oregon", "/Attachments/AllReports/state-of-alice-report-oregon-2025.pdf"),
        ("Pennsylvania", "/Attachments/AllReports/state-of-alice-report-pennsylvania-2025.pdf"),
        ("South Carolina", "/Attachments/AllReports/state-of-alice-report-south-carolina-2025.pdf"),
        ("Tennessee", "/Attachments/AllReports/state-of-alice-report-tennessee-2025.pdf"),
        ("Texas", "/Attachments/AllReports/state-of-alice-report-texas-2025.pdf"),
        ("Virginia", "/Attachments/AllReports/state-of-alice-report-virginia-2025.pdf"),
        ("Washington", "/Attachments/AllReports/state-of-alice-report-washington-2025.pdf"),
        ("West Virginia", "/Attachments/AllReports/state-of-alice-report-west-virginia-2025.pdf"),
        ("Wisconsin", "/Attachments/AllReports/state-of-alice-report-wisconsin-2025.pdf")
    ]
    
    print(f"\n📊 Downloading {len(reports)} state reports...")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.unitedforalice.org/state-reports'
    })
    
    downloaded = 0
    failed = []
    
    for state_name, pdf_path in reports:
        url = base_url + pdf_path
        filename = f"2025 ALICE Report - {state_name}.pdf"
        
        try:
            print(f"📥 Downloading {state_name}...", end=" ")
            response = session.get(url, timeout=60, stream=True)
            
            if response.status_code == 200:
                # Check if it's actually a PDF
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' in content_type.lower() or response.content[:4] == b'%PDF':
                    # Save the file
                    output_path = desktop_path / filename
                    
                    # Download in chunks to handle large files
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                    print(f"✅ ({file_size_mb:.1f} MB)")
                    downloaded += 1
                else:
                    print(f"❌ Not a PDF")
                    failed.append(state_name)
            else:
                print(f"❌ Status {response.status_code}")
                failed.append(state_name)
                
        except requests.exceptions.Timeout:
            print(f"⏱️ Timeout")
            failed.append(state_name)
        except Exception as e:
            print(f"❌ Error: {str(e)[:30]}")
            failed.append(state_name)
        
        # Be respectful to the server
        time.sleep(2)
    
    print(f"\n📊 Summary:")
    print(f"   ✅ Successfully downloaded: {downloaded} reports")
    if failed:
        print(f"   ❌ Failed to download: {len(failed)} reports")
        print(f"      {', '.join(failed)}")
    
    print(f"\n📁 Reports saved to: {desktop_path}")
    
    # Create a README file
    readme_path = desktop_path / "README.txt"
    with open(readme_path, 'w') as f:
        f.write("ALICE State Reports Collection (2025)\n")
        f.write("="*40 + "\n\n")
        f.write(f"Downloaded: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total Reports Downloaded: {downloaded}\n\n")
        f.write("These reports contain comprehensive data about ALICE\n")
        f.write("(Asset Limited, Income Constrained, Employed) households.\n\n")
        f.write("Source: United For ALICE (www.unitedforalice.org)\n\n")
        
        if downloaded > 0:
            f.write("States with reports:\n")
            for state, _ in reports:
                if state not in failed:
                    f.write(f"  • {state}\n")
        
        if failed:
            f.write("\nStates not downloaded (may need manual download):\n")
            for state in failed:
                f.write(f"  • {state}\n")
    
    print(f"📝 Created README.txt")
    
    # Open the folder in Finder
    os.system(f'open "{desktop_path}"')
    
    return desktop_path

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   ALICE PDF REPORT DOWNLOADER             ║
    ║   Downloading all 2025 state reports       ║
    ╚════════════════════════════════════════════╝
    """)
    
    folder_path = download_alice_reports()
    
    print(f"""
    ✅ Process complete!
    
    The folder has been opened in Finder.
    
    Note: If some reports failed, they may require
    manual download from www.unitedforalice.org
    """)