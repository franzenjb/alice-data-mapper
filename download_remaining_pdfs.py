#!/usr/bin/env python3
"""
Download remaining ALICE state PDF reports (starting from Louisiana)
"""

import requests
import os
from pathlib import Path
import time

def download_remaining_reports():
    """Download remaining ALICE state PDF reports"""
    
    # Use existing folder on Desktop
    desktop_path = Path.home() / "Desktop" / "ALICE State Reports 2025"
    desktop_path.mkdir(exist_ok=True)
    
    print(f"📁 Using folder: {desktop_path}")
    
    # Base URL
    base_url = "https://www.unitedforalice.org"
    
    # Remaining reports (starting from Louisiana)
    remaining_reports = [
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
    
    print(f"\n📊 Downloading {len(remaining_reports)} remaining state reports...")
    print("Starting from Louisiana...\n")
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/pdf,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.unitedforalice.org/state-reports'
    })
    
    downloaded = 0
    failed = []
    already_downloaded = 14  # Previously downloaded
    
    for state_name, pdf_path in remaining_reports:
        url = base_url + pdf_path
        filename = f"2025 ALICE Report - {state_name}.pdf"
        output_path = desktop_path / filename
        
        # Skip if already exists
        if output_path.exists():
            print(f"⏭️  Skipping {state_name} (already exists)")
            already_downloaded += 1
            continue
        
        try:
            print(f"📥 Downloading {state_name}...", end=" ")
            response = session.get(url, timeout=60, stream=True)
            
            if response.status_code == 200:
                # Check if it's actually a PDF
                content_type = response.headers.get('Content-Type', '')
                if 'pdf' in content_type.lower() or response.content[:4] == b'%PDF':
                    # Save the file
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
        time.sleep(3)
    
    # Count total files
    total_pdfs = len(list(desktop_path.glob("*.pdf")))
    
    print(f"\n📊 Final Summary:")
    print(f"   📁 Total PDFs in folder: {total_pdfs}")
    print(f"   ✅ Newly downloaded: {downloaded} reports")
    print(f"   📚 Previously downloaded: 14 reports")
    
    if failed:
        print(f"   ❌ Failed to download: {len(failed)} reports")
        print(f"      {', '.join(failed)}")
    
    print(f"\n📁 All reports saved to: {desktop_path}")
    
    # Update README
    readme_path = desktop_path / "README.txt"
    with open(readme_path, 'w') as f:
        f.write("ALICE State Reports Collection (2025)\n")
        f.write("="*40 + "\n\n")
        f.write(f"Last Updated: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"Total Reports: {total_pdfs}\n\n")
        f.write("These reports contain comprehensive data about ALICE\n")
        f.write("(Asset Limited, Income Constrained, Employed) households.\n\n")
        f.write("Source: United For ALICE (www.unitedforalice.org)\n\n")
        
        # List all PDF files
        pdf_files = sorted([f.stem.replace("2025 ALICE Report - ", "") for f in desktop_path.glob("*.pdf")])
        if pdf_files:
            f.write("Downloaded Reports:\n")
            for state in pdf_files:
                f.write(f"  • {state}\n")
        
        if failed:
            f.write("\nFailed Downloads (may require manual download):\n")
            for state in failed:
                f.write(f"  • {state}\n")
    
    print(f"📝 Updated README.txt")
    
    return desktop_path, total_pdfs

if __name__ == "__main__":
    print("""
    ╔════════════════════════════════════════════╗
    ║   ALICE PDF REPORT DOWNLOADER             ║
    ║   Downloading remaining reports            ║
    ╚════════════════════════════════════════════╝
    """)
    
    folder_path, total = download_remaining_reports()
    
    print(f"""
    ✅ Process complete!
    
    Total reports in folder: {total}
    Location: {folder_path}
    
    The complete collection of ALICE state reports
    is now available on your Desktop.
    """)