import csv
import re
import glob
import sys
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def auto_scrape_starlink():
    # 1. Find all HTML files
    files = glob.glob("*.html")
    if not files:
        print("Error: No .html files found in this folder.")
        return

    # 2. Interactive Selection Prompt
    print("Found the following files:")
    for i, file_name in enumerate(files):
        print(f"[{i + 1}] {file_name}")

    try:
        selection = input("\nEnter the number of the file to scrape: ")
        idx = int(selection) - 1
        
        if idx < 0 or idx >= len(files):
            print("Invalid selection. Exiting.")
            return
            
        file_path = files[idx]
        print(f"\nProcessing: {file_path}")
        
    except ValueError:
        print("Invalid input. Please enter a number. Exiting.")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 3. Get Total Usage from the UI text
    total_gb = 459.0  # Default fallback
    all_p = soup.find_all('p')
    for i, p in enumerate(all_p):
        if 'Total Data Usage' in p.text:
            try:
                # Assuming the value is in the next paragraph tag
                total_gb = float(all_p[i + 1].text.replace('GB', '').strip())
            except:
                pass

    # 4. Get Bar Heights (Filtering to only include positive values to ignore shadow bars)
    bars = soup.find_all('rect', class_='MuiBarElement-series-y_0')
    heights = [float(b.get('height', 0)) for b in bars if float(b.get('height', 0)) > 0]

    # 5. Calculate Ratio
    if sum(heights) == 0:
        print("Error: Could not calculate usage ratio (sum of bar heights is 0).")
        return
    gb_per_pixel = total_gb / sum(heights)

    # 6. Auto-detect Billing Cycle Start
    start_date = datetime.today().replace(day=17)
    for p in all_p:
        match = re.search(r'(\d{1,2})/(\d{1,2})/(\d{4})', p.text)
        if match:
            last_upd = datetime(int(match.group(3)), int(match.group(1)), int(match.group(2)))
            start_date = last_upd.replace(day=17)
            if last_upd.day < 17:
                # If current date is before the 17th, billing cycle started last month
                if start_date.month == 1:
                    start_date = start_date.replace(year=start_date.year - 1, month=12)
                else:
                    start_date = start_date.replace(month=start_date.month - 1)
            break

    # 7. Export
    with open('data_usage.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Data Usage (GB)'])
        for i, h in enumerate(heights):
            date_str = (start_date + timedelta(days=i)).strftime('%m/%d/%Y')
            writer.writerow([date_str, round(h * gb_per_pixel, 2)])

    print(f"Success! Data exported for cycle starting {start_date.strftime('%B %d, %Y')}")

if __name__ == '__main__':
    auto_scrape_starlink()
