import csv
import re
import glob
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def process_file(file_path):
    """Extracts data and automatically anchors the date to the billing cycle."""
    with open(file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    # 1. Get Total Usage
    total_gb = 459.0
    all_p = soup.find_all('p')
    for i, p in enumerate(all_p):
        if 'Total Data Usage' in p.text:
            try:
                total_gb = float(all_p[i + 1].text.replace('GB', '').strip())
            except: pass

    # 2. Get Bar Heights (keep all bars, including zero-usage days)
    bars = soup.find_all('rect', class_='MuiBarElement-series-y_0')
    heights = [float(b.get('height', 0)) for b in bars]

    if not heights: return None, None
    gb_per_pixel = total_gb / sum(heights)

    # 3. Detect active month — the class "1bcwr2w" is on the <h6> inside the
    #    button, NOT on the button itself, so we select h6[class*="1bcwr2w"]
    month_map = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4,
        "May": 5, "Jun": 6, "Jul": 7, "Aug": 8,
        "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12
    }
    active_h6 = soup.select_one('h6[class*="1bcwr2w"]')
    active_month = active_h6.text.strip() if active_h6 else None
    m_num = month_map.get(active_month, datetime.now().month)

    # 4. Extract year from a date-formatted <p> tag (e.g. "5/21/2026, 8:09:57 AM")
    year = datetime.now().year
    for p in all_p:
        match = re.search(r'\d{1,2}/\d{1,2}/(\d{4})', p.text)
        if match:
            year = int(match.group(1))
            break

    start_date = datetime(year, m_num, 17)

    # 5. Map rows
    data_rows = []
    for i, h in enumerate(heights):
        date_obj = start_date + timedelta(days=i)
        data_rows.append({
            'Date': date_obj.strftime('%m/%d/%Y'),
            'GB': round(h * gb_per_pixel, 2)
        })

    return total_gb, data_rows


def auto_scrape_starlink():
    files = glob.glob("*.html")
    if not files:
        print("Error: No .html files found.")
        return

    print("Found files:")
    for i, f in enumerate(files): print(f"  [{i + 1}] {f}")
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
        print(f"Processing: {file_path}")
        total, rows = process_file(file_path)
        if rows:
            grand_total += total
            for r in rows:
                all_data[r['Date']] = all_data.get(r['Date'], 0) + r['GB']

    # Export to CSV
    with open('data_usage.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Date', 'Data Usage (GB)'])

        sorted_dates = sorted(all_data.keys(), key=lambda d: datetime.strptime(d, '%m/%d/%Y'))
        for date_key in sorted_dates:
            writer.writerow([date_key, round(all_data[date_key], 2)])

        writer.writerow([])
        writer.writerow(['Total Usage', round(grand_total, 2)])

    print(f"\nSuccess! Exported to 'data_usage.csv'.")
    print(f"Grand Total Usage: {round(grand_total, 2)} GB")


if __name__ == '__main__':
    auto_scrape_starlink()
