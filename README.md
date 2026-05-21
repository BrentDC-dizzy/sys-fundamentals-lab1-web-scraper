# Starlink Usage Scraper

A Python utility that extracts structured daily data usage from a saved Starlink account dashboard HTML file. The script converts the visual bar chart into accurate, readable CSV data mapped to your billing cycle.

---

## How It Works

1. Reads the total data usage displayed on the page to establish a GB baseline.
2. Calculates a pixel-to-GB ratio from the bar chart heights.
3. Anchors the billing cycle to the **17th of the month** and maps each bar to its correct calendar date.
4. Exports the result to `data_usage.csv`.

---

## Requirements

- Python 3.x
- [beautifulsoup4](https://pypi.org/project/beautifulsoup4/) — HTML parsing

---

## Setup

**1. Install the dependency**

```bash
pip install beautifulsoup4
```

**2. Add your HTML file**

Save your Starlink account page as an HTML file and place it in the same folder as `scraper.py`. Any `.html` file in the folder will be picked up automatically.

**3. Run the scraper**

```bash
python scraper.py
```

---

## Output

Generates `data_usage.csv` with two columns:

| Date | Data Usage (GB) |
|---|---|
| 04/17/2026 | 22.79 |
| 04/18/2026 | 18.42 |
| … | … |

---

## Notes

- The script anchors to the **17th** as the billing cycle start date. If the "Last Updated" timestamp on the page falls before the 17th, it automatically rolls back to the previous month's 17th.
- The pixel-to-GB ratio is derived from the page's own **Total Data Usage** figure, so the sum of all daily values will match exactly what Starlink reports.

---

## Dependencies

```
beautifulsoup4
```
