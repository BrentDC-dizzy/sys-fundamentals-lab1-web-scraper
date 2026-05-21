import csv
import re
import glob
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def process_file(file_path):
    """Extracts data and dynamically anchors the date to the billing cycle."""
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. Get Total Usage
    total_gb = 459.0
    all_p = soup.find_all('p')
    for i, p in enumerate(all_p):
        if 'Total Data Usage' in p.text:
            try:
                total_gb = float(all_p[i + 1].text.replace('GB', '').strip())
            except: 
                pass

    # 2. Get Bar Heights (Filtered to only positive usage days)
    bars = soup.find_all('rect', class_='MuiBarElement-series-y_0')
    heights = [float(b.get('height', 0)) for b in bars if float(b.get('height', 0)) > 0]
    
    if not heights: 
        return None, None
    gb_per_pixel = total_gb / sum(heights)

    # 3. Detect Start Date using active UI element
    # Looks for buttons with aria-pressed="true" to find the selected month
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, 
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    
    active_btn = soup.select_one('button[aria-pressed="true"]') or soup.select_one('button[aria-selected="true"]')
    active_month = active_btn.get_text().strip() if active_btn else None
    
    # Fallback to current month if detection fails
    m_num = month_map.get(active_month, datetime.now().month)
    
    # Extract year from the page text
    year = datetime.now().year
    year_match = re.search(r'\d{1,2}/\d{1,2}/(\d{4})', soup.get_text())
    if year_match: 
        year = int(year_match.group(1))
    
    start_date = datetime(year, m_num, 17)

    # 4. Map rows
    data_rows = []
    for i, h in enumerate(heights):
        date_obj = start_date + timedelta(days=i)
        data_rows.append({
            'Date': date_obj.strftime('%m/%d/%Y'), 
            'GB': round(h * gb_per_pixel, 2)
        })
    
    return total_gb, data_rows

def auto_scrape_starlink():
    # Force script to look in its own directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    files = glob.glob(os.path.join(script_dir, "*.html"))
    
    if not files:
        print(f"Error: No .html files found in {script_dir}")
        return

    print("Found files:")
    for i, f in enumerate(files): 
        print(f"  [{i + 1}] {os.path.basename(f)}")
    print("  [0] Scrape ALL files")

    selection = input("\nSelect option: ")
    to_process = []
    
    if selection == '0':
        to_process = files
    else:
        try:
            to_process = [files[int(selection) - 1]]
        except:
            print("Invalid selection.")
            return

    all_data = {} 
    grand_total = 0.0

    for file_path in to_process:
        print(f"Processing: {os.path.basename(file_path)}")
        total, rows = process_file(file_path)
        if rows:
            grand_total += total
            for r in rows:
                all_data[r['Date']] = all_data.get(r['Date'], 0) + r['GB']

    # Export to CSV
    try:
        with open('data_usage.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Date', 'Data Usage (GB)'])
            
            # Sort by date
            sorted_dates = sorted(all_data.keys(), key=lambda d: datetime.strptime(d, '%m/%d/%Y'))
            for date_key in sorted_dates:
                writer.writerow([date_key, round(all_data[date_key], 2)])
            
            writer.writerow([])
            writer.writerow(['Total Usage', round(grand_total, 2)])
            
        print(f"\nSuccess! Exported to 'data_usage.csv'.")
        print(f"Grand Total Usage: {round(grand_total, 2)} GB")
        
    except PermissionError:
        print("\nError: Could not save 'data_usage.csv'. Please close the file if it is open in Excel.")

if __name__ == '__main__':
    auto_scrape_starlink()
